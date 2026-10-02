from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.audit import AuditLog
from app.models.organization import User
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/organizations/{organization_id}/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: Session = Depends(get_db),
) -> list[AuditLogRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.organization_manage):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing organization manage permission")

    statement = (
        select(AuditLog)
        .where(AuditLog.organization_id == str(organization_id))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return [AuditLogRead.model_validate(log, from_attributes=True) for log in db.scalars(statement)]
