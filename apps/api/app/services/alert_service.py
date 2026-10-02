import hashlib
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utcnow
from app.models.alert import Alert
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.schemas.alerts import AlertIngestRequest, AlertIngestResponse
from app.schemas.incidents import IncidentCreate
from app.services.audit_service import AuditService
from app.services.incident_service import IncidentService

SEVERITY_ORDER = [IncidentSeverity.low, IncidentSeverity.medium, IncidentSeverity.high, IncidentSeverity.critical]
# Incidents in these states no longer absorb new alerts; a recurrence opens a new incident.
CLOSED_STATUSES = (IncidentStatus.resolved, IncidentStatus.archived)


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def ingest(self, organization_id: UUID, request: AlertIngestRequest) -> AlertIngestResponse:
        org = str(organization_id)
        dedupe_key = self._build_dedupe_key(request)

        # Webhook senders retry; the same (source, external_id) is accepted once.
        existing = self.db.scalar(
            select(Alert).where(
                Alert.organization_id == org,
                Alert.source == request.source,
                Alert.external_id == request.external_id,
            )
        )
        if existing is not None:
            return AlertIngestResponse(
                alert_id=existing.id,
                accepted=True,
                dedupe_key=existing.fingerprint,
                incident_id=existing.incident_id,
                deduplicated=True,
                duplicate_delivery=True,
            )

        summary = request.payload.get("summary")
        alert = Alert(
            organization_id=org,
            source=request.source,
            external_id=request.external_id,
            title=request.title,
            fingerprint=dedupe_key,
            payload=request.payload,
            summary=summary if isinstance(summary, str) else None,
        )
        severity = self._severity_from_payload(request.payload)
        incidents = IncidentService(self.db)

        open_incident = self.db.scalar(
            select(Incident)
            .where(
                Incident.organization_id == org,
                Incident.dedupe_key == dedupe_key,
                Incident.status.not_in(CLOSED_STATUSES),
            )
            .order_by(Incident.created_at.desc())
            .limit(1)
        )

        if open_incident is None:
            self.db.add(alert)
            self.db.flush()
            incident = incidents.create_incident(
                organization_id=organization_id,
                request=IncidentCreate(
                    title=request.title,
                    description=alert.summary,
                    severity=severity,
                    dedupe_key=dedupe_key,
                ),
                actor_id=None,
            )
            alert.incident_id = str(incident.id)
            self.db.commit()
            return AlertIngestResponse(
                alert_id=alert.id, accepted=True, dedupe_key=dedupe_key, incident_id=incident.id
            )

        # Group the alert into the open incident instead of opening a new one.
        alert.incident_id = str(open_incident.id)
        self.db.add(alert)
        self.db.flush()
        note = f"Duplicate alert received from {request.source.value} ({request.external_id})."
        if SEVERITY_ORDER.index(severity) > SEVERITY_ORDER.index(open_incident.severity):
            note += f" Severity raised from {open_incident.severity.value} to {severity.value}."
            open_incident.severity = severity
        open_incident.updated_at = utcnow()
        incidents.add_timeline_event(
            incident_id=open_incident.id, actor_id=None, event_type="alert.grouped", body=note
        )
        AuditService(self.db).record(
            organization_id=organization_id,
            actor_id=None,
            action="alert.grouped",
            target_type="incident",
            target_id=open_incident.id,
            metadata={"alert_id": str(alert.id), "source": request.source.value},
        )
        self.db.commit()
        return AlertIngestResponse(
            alert_id=alert.id,
            accepted=True,
            dedupe_key=dedupe_key,
            incident_id=open_incident.id,
            deduplicated=True,
        )

    def list_alerts(self, organization_id: UUID, limit: int = 50, offset: int = 0) -> list[Alert]:
        statement = (
            select(Alert)
            .where(Alert.organization_id == str(organization_id))
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(statement))

    def list_incident_alerts(self, organization_id: UUID, incident_id: UUID) -> list[Alert]:
        statement = (
            select(Alert)
            .where(Alert.organization_id == str(organization_id), Alert.incident_id == str(incident_id))
            .order_by(Alert.created_at.asc())
        )
        return list(self.db.scalars(statement))

    @staticmethod
    def _build_dedupe_key(request: AlertIngestRequest) -> str:
        service = str(request.payload.get("service", "unknown-service")).lower()
        env = str(request.payload.get("environment", "unknown-env")).lower()
        raw = f"{request.source.value}:{service}:{env}:{request.title.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def _severity_from_payload(payload: dict) -> IncidentSeverity:
        value = str(payload.get("severity", "medium")).lower()
        if value in {item.value for item in IncidentSeverity}:
            return IncidentSeverity(value)
        return IncidentSeverity.medium
