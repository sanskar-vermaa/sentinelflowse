from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        organization_id: UUID | str,
        action: str,
        target_type: str,
        target_id: UUID | str | None = None,
        actor_id: UUID | str | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            organization_id=str(organization_id),
            actor_id=str(actor_id) if actor_id is not None else None,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            metadata_json=metadata or {},
        )
        self.db.add(log)
        return log

