from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import WorkflowRunStatus


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    trigger: str = Field(min_length=2, max_length=80)
    definition: dict


class WorkflowRunRead(BaseModel):
    id: UUID
    workflow_id: UUID
    incident_id: UUID | None
    status: WorkflowRunStatus
    output_payload: dict | None

