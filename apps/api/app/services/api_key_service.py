import secrets
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.api_key import ApiKey


@dataclass(frozen=True)
class CreatedApiKey:
    record: ApiKey
    secret: str


class ApiKeyService:
    def __init__(self, db: Session):
        self.db = db

    def create_key(self, organization_id: UUID, name: str) -> CreatedApiKey:
        secret = f"sf_{secrets.token_urlsafe(32)}"
        record = ApiKey(
            organization_id=str(organization_id),
            name=name,
            key_prefix=secret[:12],
            key_hash=hash_password(secret),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return CreatedApiKey(record=record, secret=secret)

    def authenticate(self, secret: str) -> ApiKey | None:
        prefix = secret[:12]
        candidates = self.db.scalars(select(ApiKey).where(ApiKey.key_prefix == prefix, ApiKey.revoked_at.is_(None)))
        for candidate in candidates:
            if verify_password(secret, candidate.key_hash):
                return candidate
        return None
