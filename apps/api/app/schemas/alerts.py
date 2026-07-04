from uuid import UUID

from pydantic import BaseModel, Field

from app.models.alert import AlertSource


class AlertIngestRequest(BaseModel):
    source: AlertSource
    external_id: str = Field(min_length=1, max_length=180)
    title: str = Field(min_length=3, max_length=240)
    payload: dict


class AlertIngestResponse(BaseModel):
    alert_id: UUID
    accepted: bool
    dedupe_key: str
    incident_id: UUID | None = None

