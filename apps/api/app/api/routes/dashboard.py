from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.organization import User
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/organizations/{organization_id}/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> dict[str, int]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing read permission")
    return DashboardService(db).organization_summary(organization_id)

