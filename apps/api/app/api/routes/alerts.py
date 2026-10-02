from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.organization import User
from app.schemas.alerts import AlertIngestRequest, AlertIngestResponse, AlertRead
from app.services.alert_service import AlertService
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/alerts", tags=["alerts"])
org_router = APIRouter(prefix="/organizations/{organization_id}/alerts", tags=["alerts"])


@org_router.get("", response_model=list[AlertRead])
def list_alerts(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[AlertRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing alert read permission")

    alerts = AlertService(db).list_alerts(organization_id, limit=limit, offset=offset)
    return [AlertRead.model_validate(alert, from_attributes=True) for alert in alerts]


@router.post("/ingest", response_model=AlertIngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_alert(
    request: AlertIngestRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> AlertIngestResponse:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    api_key = ApiKeyService(db).authenticate(x_api_key)
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return AlertService(db).ingest(api_key.organization_id, request)
