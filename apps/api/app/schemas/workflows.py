from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import WorkflowRunStatus


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    trigger: str = Field(min_length=2, max_length=80)
    definition: dict


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    is_enabled: bool | None = None


class WorkflowRunCreate(BaseModel):
    incident_id: UUID | None = None


class WorkflowRunRead(BaseModel):
    id: UUID
    workflow_id: UUID
    incident_id: UUID | None
    status: WorkflowRunStatus
    output_payload: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRead(BaseModel):
    id: UUID
    name: str
    trigger: str
    definition: dict
    is_enabled: bool

    model_config = {"from_attributes": True}
