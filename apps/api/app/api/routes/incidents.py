from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.incident import IncidentStatus
from app.models.organization import User
from app.schemas.alerts import AlertRead
from app.schemas.incidents import (
    IncidentCreate,
    IncidentRead,
    IncidentTimelineEventRead,
    IncidentUpdate,
    TriageRead,
)
from app.services.alert_service import AlertService
from app.services.incident_service import IncidentListFilters, IncidentService
from app.services.triage_service import TriageRequest, TriageService

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
    if request.assignee_id is not None and get_membership(db, request.assignee_id, organization_id) is None:
        raise HTTPException(status_code=422, detail="Assignee is not a member of this organization")

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


@router.get("/{incident_id}/alerts", response_model=list[AlertRead])
def list_incident_alerts(
    organization_id: UUID,
    incident_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[AlertRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident read permission")
    if IncidentService(db).get_incident(organization_id, incident_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    alerts = AlertService(db).list_incident_alerts(organization_id, incident_id)
    return [AlertRead.model_validate(alert, from_attributes=True) for alert in alerts]


@router.post("/{incident_id}/triage", response_model=TriageRead)
def triage_incident(
    organization_id: UUID,
    incident_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TriageRead:
    """Ask the AI (or the built-in playbook) for a summary and next steps.

    The suggestion is also recorded on the incident timeline.
    """
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_write):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing incident write permission")

    incidents = IncidentService(db)
    incident = incidents.get_incident(organization_id, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    alerts = AlertService(db).list_incident_alerts(organization_id, incident_id)
    events = incidents.list_timeline_events(organization_id, incident_id)
    result = TriageService().suggest(
        TriageRequest(
            title=incident.title,
            severity=incident.severity.value,
            summary=incident.description,
            status=incident.status.value,
            alert_sources=[f"{a.source.value}:{a.external_id}" for a in alerts],
            timeline=[f"{e.event_type}: {e.body}" for e in events],
        )
    )
    body = result.summary + "\n" + "\n".join(f"- {action}" for action in result.recommended_actions)
    incidents.add_timeline_event(incident_id=incident.id, actor_id=current_user.id, event_type="ai.triage", body=body)
    db.commit()
    return TriageRead(provider=result.provider, summary=result.summary, recommended_actions=result.recommended_actions)
