from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.db.base import Base
from app.models.incident import Incident, IncidentSeverity, IncidentStatus, IncidentTimelineEvent
from app.models.organization import Organization
from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStatus
from sentinelflow_worker.runner import Worker


@pytest.fixture
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/worker.db")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def seed_run(factory, steps):
    db = factory()
    org = Organization(name="Acme", slug=f"acme-{uuid4().hex[:6]}")
    db.add(org)
    db.flush()
    incident = Incident(
        organization_id=str(org.id),
        title="API errors",
        severity=IncidentSeverity.medium,
        status=IncidentStatus.open,
        dedupe_key="api-errors-key",
    )
    workflow = Workflow(organization_id=str(org.id), name="Escalate", trigger="incident.created", definition={"steps": steps})
    db.add_all([incident, workflow])
    db.flush()
    run = WorkflowRun(
        workflow_id=str(workflow.id), incident_id=str(incident.id), status=WorkflowRunStatus.queued, input_payload={}
    )
    db.add(run)
    db.commit()
    ids = (run.id, incident.id)
    db.close()
    return ids


def test_tick_executes_queued_runs(session_factory):
    run_id, incident_id = seed_run(
        session_factory, [{"type": "notify", "channel": "on-call"}, {"type": "escalate", "severity": "critical"}]
    )
    assert Worker(session_factory).tick() == 1

    db = session_factory()
    run = db.get(WorkflowRun, run_id)
    assert run.status == WorkflowRunStatus.succeeded
    assert len(run.output_payload["steps"]) == 2
    assert db.get(Incident, incident_id).severity == IncidentSeverity.critical
    events = db.query(IncidentTimelineEvent).filter_by(event_type="workflow.step").count()
    assert events == 2


def test_failed_steps_mark_the_run_failed(session_factory):
    run_id, _ = seed_run(session_factory, [{"type": "teleport"}])
    Worker(session_factory).tick()
    run = session_factory().get(WorkflowRun, run_id)
    assert run.status == WorkflowRunStatus.failed
    assert "unknown step type" in run.output_payload["error"]


def test_idle_worker_sleeps_between_polls(session_factory):
    naps = []
    worker = Worker(session_factory, poll_seconds=1.5, sleep=naps.append)
    worker.run(max_ticks=3)
    assert naps == [1.5, 1.5, 1.5]


def test_stop_ends_the_loop(session_factory):
    worker = Worker(session_factory, sleep=lambda _s: worker.stop())
    worker.run(max_ticks=100)
    assert worker.running is False


def test_tick_survives_database_errors():
    class Broken:
        def get_bind(self):
            raise RuntimeError("db down")

        def rollback(self):
            pass

        def close(self):
            pass

    assert Worker(lambda: Broken()).tick() == 0
