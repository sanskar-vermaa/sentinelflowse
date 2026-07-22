from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStatus
from app.schemas.workflows import WorkflowCreate


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def create_workflow(self, organization_id: UUID, request: WorkflowCreate) -> Workflow:
        workflow = Workflow(
            organization_id=str(organization_id),
            name=request.name,
            trigger=request.trigger,
            definition=request.definition,
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def list_workflows(self, organization_id: UUID) -> list[Workflow]:
        statement = select(Workflow).where(Workflow.organization_id == str(organization_id)).order_by(Workflow.created_at.desc())
        return list(self.db.scalars(statement))

    def create_run(self, workflow_id: UUID, incident_id: UUID | None, input_payload: dict) -> WorkflowRun:
        run = WorkflowRun(
            workflow_id=str(workflow_id),
            incident_id=str(incident_id) if incident_id else None,
            status=WorkflowRunStatus.queued,
            input_payload=input_payload,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

