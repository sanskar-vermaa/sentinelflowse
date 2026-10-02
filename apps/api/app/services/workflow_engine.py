"""Workflow automation: queue runs on incident events and execute them.

Definitions look like:

    {
      "conditions": {"min_severity": "high"},          # optional
      "steps": [
        {"type": "notify", "channel": "on-call"},
        {"type": "timeline", "message": "Runbook started"},
        {"type": "escalate", "severity": "critical"}
      ]
    }

Runs are queued when an incident event matches a workflow's trigger and are
executed by the worker (or inline, with WORKFLOW_EXECUTION=inline).
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentSeverity
from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStatus
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

TRIGGERS = ("incident.created", "incident.updated", "incident.resolved", "manual")
STEP_TYPES = ("notify", "timeline", "escalate")
SEVERITY_ORDER = [
    s.value for s in (IncidentSeverity.low, IncidentSeverity.medium, IncidentSeverity.high, IncidentSeverity.critical)
]
MAX_STEPS = 20


class InvalidDefinition(ValueError):
    pass


def validate_definition(trigger: str, definition: dict) -> None:
    if trigger not in TRIGGERS:
        raise InvalidDefinition(f"Unknown trigger '{trigger}'. Use one of: {', '.join(TRIGGERS)}.")
    steps = definition.get("steps")
    if not isinstance(steps, list) or not steps:
        raise InvalidDefinition("Definition needs a non-empty 'steps' list.")
    if len(steps) > MAX_STEPS:
        raise InvalidDefinition(f"A workflow can have at most {MAX_STEPS} steps.")
    for i, step in enumerate(steps, start=1):
        if not isinstance(step, dict) or step.get("type") not in STEP_TYPES:
            raise InvalidDefinition(f"Step {i}: type must be one of {', '.join(STEP_TYPES)}.")
        if step["type"] == "notify" and not isinstance(step.get("channel"), str):
            raise InvalidDefinition(f"Step {i}: notify needs a 'channel'.")
        if step["type"] == "timeline" and not isinstance(step.get("message"), str):
            raise InvalidDefinition(f"Step {i}: timeline needs a 'message'.")
        if step["type"] == "escalate" and step.get("severity") not in SEVERITY_ORDER:
            raise InvalidDefinition(f"Step {i}: escalate needs a valid 'severity'.")
    conditions = definition.get("conditions", {})
    if not isinstance(conditions, dict):
        raise InvalidDefinition("'conditions' must be an object.")
    min_sev = conditions.get("min_severity")
    if min_sev is not None and min_sev not in SEVERITY_ORDER:
        raise InvalidDefinition("conditions.min_severity must be a valid severity.")


def _matches(workflow: Workflow, incident: Incident) -> bool:
    min_sev = (workflow.definition or {}).get("conditions", {}).get("min_severity")
    if min_sev is None:
        return True
    return SEVERITY_ORDER.index(incident.severity.value) >= SEVERITY_ORDER.index(min_sev)


class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db

    def enqueue_for_event(self, organization_id: UUID | str, event: str, incident: Incident) -> list[WorkflowRun]:
        """Queue a run for each enabled workflow whose trigger and conditions match. Does not commit."""
        workflows = self.db.scalars(
            select(Workflow).where(
                Workflow.organization_id == str(organization_id),
                Workflow.trigger == event,
                Workflow.is_enabled.is_(True),
            )
        )
        runs = []
        for workflow in workflows:
            if not _matches(workflow, incident):
                continue
            run = WorkflowRun(
                workflow_id=str(workflow.id),
                incident_id=str(incident.id),
                status=WorkflowRunStatus.queued,
                input_payload={"event": event, "incident_id": str(incident.id)},
            )
            self.db.add(run)
            runs.append(run)
        return runs

    def process_queued(self, limit: int = 20) -> int:
        """Execute up to `limit` queued runs. Returns how many were processed."""
        statement = (
            select(WorkflowRun)
            .where(WorkflowRun.status == WorkflowRunStatus.queued)
            .order_by(WorkflowRun.created_at.asc())
            .limit(limit)
        )
        if self.db.get_bind().dialect.name == "postgresql":
            # Several workers can poll safely: each run is claimed once.
            statement = statement.with_for_update(skip_locked=True)
        runs = list(self.db.scalars(statement))
        for run in runs:
            run.status = WorkflowRunStatus.running
        self.db.commit()
        for run in runs:
            self.execute(run)
        return len(runs)

    def execute(self, run: WorkflowRun) -> WorkflowRun:
        from app.services.incident_service import (
            IncidentService,  # avoid an import cycle
        )

        workflow = self.db.get(Workflow, UUID(str(run.workflow_id)))
        incident = self.db.get(Incident, UUID(str(run.incident_id))) if run.incident_id else None
        results: list[dict] = []
        try:
            if workflow is None:
                raise RuntimeError("workflow no longer exists")
            incidents = IncidentService(self.db)
            for step in workflow.definition.get("steps", []):
                kind = step.get("type")
                if kind == "notify":
                    message = f"Workflow '{workflow.name}' notified {step['channel']}."
                elif kind == "timeline":
                    message = f"Workflow '{workflow.name}': {step['message']}"
                elif kind == "escalate":
                    if incident is None:
                        raise RuntimeError("escalate needs an incident")
                    target = step["severity"]
                    if SEVERITY_ORDER.index(target) > SEVERITY_ORDER.index(incident.severity.value):
                        message = (
                            f"Workflow '{workflow.name}' raised severity from {incident.severity.value} to {target}."
                        )
                        incident.severity = IncidentSeverity(target)
                    else:
                        message = f"Workflow '{workflow.name}' left severity at {incident.severity.value}."
                else:
                    raise RuntimeError(f"unknown step type {kind!r}")
                if incident is not None:
                    incidents.add_timeline_event(
                        incident_id=incident.id, actor_id=None, event_type="workflow.step", body=message
                    )
                results.append({"type": kind, "result": message})
            run.status = WorkflowRunStatus.succeeded
            run.output_payload = {"steps": results}
        except Exception as exc:
            logger.warning("Workflow run %s failed: %s", run.id, exc)
            run.status = WorkflowRunStatus.failed
            run.output_payload = {"steps": results, "error": str(exc)}
        if workflow is not None:
            AuditService(self.db).record(
                organization_id=workflow.organization_id,
                action=f"workflow.run.{run.status.value}",
                target_type="workflow_run",
                target_id=run.id,
                metadata={"workflow_id": str(workflow.id)},
            )
        self.db.commit()
        return run
