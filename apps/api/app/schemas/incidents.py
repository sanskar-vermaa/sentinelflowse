from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.incident import IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    description: str | None = None
    severity: IncidentSeverity
    dedupe_key: str = Field(min_length=8, max_length=128)


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    severity: IncidentSeverity | None = None
    assignee_id: UUID | None = None


class IncidentRead(BaseModel):
    id: UUID
    title: str
    description: str | None
    severity: IncidentSeverity
    status: IncidentStatus
    assignee_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentTransitionResponse(BaseModel):
    incident: IncidentRead
    timeline_event_count: int


class IncidentTimelineEventRead(BaseModel):
    id: UUID
    incident_id: UUID
    actor_id: UUID | None
    event_type: str
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TriageRead(BaseModel):
    provider: str
    summary: str
    recommended_actions: list[str]
