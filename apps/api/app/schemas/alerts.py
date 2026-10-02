from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.alert import AlertSource


class AlertIngestRequest(BaseModel):
    source: AlertSource
    external_id: str = Field(min_length=1, max_length=180)
    title: str = Field(min_length=3, max_length=240)
    payload: dict = Field(default_factory=dict)


class AlertIngestResponse(BaseModel):
    alert_id: UUID
    accepted: bool
    dedupe_key: str
    incident_id: UUID | None = None
    # True when the alert was grouped into an existing open incident.
    deduplicated: bool = False
    # True when this exact alert (same source and external_id) was already received.
    duplicate_delivery: bool = False


class AlertRead(BaseModel):
    id: UUID
    source: AlertSource
    external_id: str
    title: str
    fingerprint: str
    summary: str | None
    incident_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

