from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: UUID
    organization_id: UUID
    actor_id: UUID | None
    action: str
    target_type: str
    target_id: str | None
    metadata_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}

