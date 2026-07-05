from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.incident import IncidentStatus
from app.models.organization import User
from app.schemas.incidents import IncidentCreate, IncidentRead, IncidentTimelineEventRead, IncidentUpdate
from app.services.incident_service import IncidentListFilters, IncidentService

router = APIRouter(prefix="/organizations/{organization_id}/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    organization_id: UUID,
    request: IncidentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> IncidentRead:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_write):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident write permission")

    incident = IncidentService(db).create_incident(organization_id, request, actor_id=current_user.id)
    return IncidentRead.model_validate(incident, from_attributes=True)


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: Annotated[IncidentStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[IncidentRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident read permission")

    incidents = IncidentService(db).list_incidents(
        IncidentListFilters(organization_id=organization_id, status=status_filter, limit=limit, offset=offset)
    )
    return [IncidentRead.model_validate(incident, from_attributes=True) for incident in incidents]


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    organization_id: UUID,
    incident_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> IncidentRead:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident read permission")

    incident = IncidentService(db).get_incident(organization_id, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return IncidentRead.model_validate(incident, from_attributes=True)


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(
    organization_id: UUID,
    incident_id: UUID,
    request: IncidentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> IncidentRead:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_write):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident write permission")

    incident = IncidentService(db).update_incident(
        organization_id=organization_id,
        incident_id=incident_id,
        request=request,
        actor_id=current_user.id,
    )
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return IncidentRead.model_validate(incident, from_attributes=True)


@router.get("/{incident_id}/timeline", response_model=list[IncidentTimelineEventRead])
def list_incident_timeline(
    organization_id: UUID,
    incident_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[IncidentTimelineEventRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident read permission")

    service = IncidentService(db)
    if service.get_incident(organization_id, incident_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    events = service.list_timeline_events(organization_id, incident_id)
    return [IncidentTimelineEventRead.model_validate(event, from_attributes=True) for event in events]
