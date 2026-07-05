from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentStatus, IncidentTimelineEvent
from app.schemas.incidents import IncidentCreate, IncidentUpdate


@dataclass(frozen=True)
class IncidentListFilters:
    organization_id: UUID
    status: IncidentStatus | None = None
    assignee_id: UUID | None = None
    limit: int = 50
    offset: int = 0


class IncidentService:
    def __init__(self, db: Session):
        self.db = db

    def create_incident(self, organization_id: UUID, request: IncidentCreate, actor_id: UUID | None) -> Incident:
        incident = Incident(
            organization_id=str(organization_id),
            title=request.title,
            description=request.description,
            severity=request.severity,
            status=IncidentStatus.open,
            dedupe_key=request.dedupe_key,
        )
        self.db.add(incident)
        self.db.flush()
        self.add_timeline_event(
            incident_id=incident.id,
            actor_id=actor_id,
            event_type="incident.created",
            body=f"Incident created with {request.severity.value} severity.",
        )
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def list_incidents(self, filters: IncidentListFilters) -> list[Incident]:
        statement: Select[tuple[Incident]] = select(Incident).where(
            Incident.organization_id == str(filters.organization_id)
        )
        if filters.status is not None:
            statement = statement.where(Incident.status == filters.status)
        if filters.assignee_id is not None:
            statement = statement.where(Incident.assignee_id == str(filters.assignee_id))
        statement = statement.order_by(Incident.updated_at.desc()).limit(filters.limit).offset(filters.offset)
        return list(self.db.scalars(statement))

    def get_incident(self, organization_id: UUID, incident_id: UUID) -> Incident | None:
        return self.db.scalar(
            select(Incident).where(
                Incident.id == incident_id,
                Incident.organization_id == str(organization_id),
            )
        )

    def list_timeline_events(self, organization_id: UUID, incident_id: UUID) -> list[IncidentTimelineEvent]:
        incident = self.get_incident(organization_id, incident_id)
        if incident is None:
            return []
        statement = (
            select(IncidentTimelineEvent)
            .where(IncidentTimelineEvent.incident_id == str(incident_id))
            .order_by(IncidentTimelineEvent.created_at.asc())
        )
        return list(self.db.scalars(statement))

    def update_incident(
        self,
        organization_id: UUID,
        incident_id: UUID,
        request: IncidentUpdate,
        actor_id: UUID | None,
    ) -> Incident | None:
        incident = self.get_incident(organization_id, incident_id)
        if incident is None:
            return None

        changes: list[str] = []
        if request.status is not None and request.status != incident.status:
            changes.append(f"status changed from {incident.status.value} to {request.status.value}")
            incident.status = request.status
        if request.severity is not None and request.severity != incident.severity:
            changes.append(f"severity changed from {incident.severity.value} to {request.severity.value}")
            incident.severity = request.severity
        if request.assignee_id is not None and str(request.assignee_id) != incident.assignee_id:
            changes.append("assignee changed")
            incident.assignee_id = str(request.assignee_id)

        if changes:
            self.add_timeline_event(
                incident_id=incident.id,
                actor_id=actor_id,
                event_type="incident.updated",
                body="; ".join(changes),
            )
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def add_timeline_event(
        self,
        incident_id: UUID,
        actor_id: UUID | None,
        event_type: str,
        body: str,
    ) -> IncidentTimelineEvent:
        event = IncidentTimelineEvent(
            incident_id=str(incident_id),
            actor_id=str(actor_id) if actor_id is not None else None,
            event_type=event_type,
            body=body,
        )
        self.db.add(event)
        return event
