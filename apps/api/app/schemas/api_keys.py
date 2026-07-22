from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class ApiKeyRead(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreateResponse(BaseModel):
    api_key: ApiKeyRead
    secret: str

