import hashlib
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import IncidentSeverity
from app.schemas.alerts import AlertIngestRequest, AlertIngestResponse
from app.schemas.incidents import IncidentCreate
from app.services.incident_service import IncidentService


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def ingest(self, organization_id: UUID, request: AlertIngestRequest) -> AlertIngestResponse:
        dedupe_key = self._build_dedupe_key(request)
        alert = Alert(
            organization_id=str(organization_id),
            source=request.source,
            external_id=request.external_id,
            title=request.title,
            fingerprint=dedupe_key,
            payload=request.payload,
            summary=request.payload.get("summary") if isinstance(request.payload.get("summary"), str) else None,
        )
        self.db.add(alert)
        self.db.flush()

        incident = IncidentService(self.db).create_incident(
            organization_id=organization_id,
            request=IncidentCreate(
                title=request.title,
                description=alert.summary,
                severity=self._severity_from_payload(request.payload),
                dedupe_key=dedupe_key,
            ),
            actor_id=None,
        )
        return AlertIngestResponse(alert_id=alert.id, accepted=True, dedupe_key=dedupe_key, incident_id=incident.id)

    def list_alerts(self, organization_id: UUID, limit: int = 50, offset: int = 0) -> list[Alert]:
        statement = (
            select(Alert)
            .where(Alert.organization_id == str(organization_id))
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .offset(offset)
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

