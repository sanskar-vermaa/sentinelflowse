from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.api_key import ApiKey
from app.models.organization import User
from app.schemas.api_keys import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyRead
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/organizations/{organization_id}/api-keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeyRead])
def list_api_keys(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[ApiKeyRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.organization_manage):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing organization manage permission")
    statement = select(ApiKey).where(ApiKey.organization_id == str(organization_id)).order_by(ApiKey.created_at.desc())
    return [ApiKeyRead.model_validate(key, from_attributes=True) for key in db.scalars(statement)]


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    organization_id: UUID,
    request: ApiKeyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ApiKeyCreateResponse:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.organization_manage):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing organization manage permission")
    created = ApiKeyService(db).create_key(organization_id, request.name)
    return ApiKeyCreateResponse(
        api_key=ApiKeyRead.model_validate(created.record, from_attributes=True),
        secret=created.secret,
    )
