from types import SimpleNamespace
from uuid import uuid4

from app.models.incident import IncidentSeverity, IncidentStatus
from app.schemas.incidents import IncidentCreate, IncidentUpdate
from app.services.incident_service import IncidentService


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.commits = 0
        self.refreshed = []

    def add(self, value) -> None:
        self.added.append(value)

    def flush(self) -> None:
        for value in self.added:
            if getattr(value, "id", None) is None:
                value.id = uuid4()

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, value) -> None:
        self.refreshed.append(value)

    def scalars(self, statement):
        return []  # no workflows configured


def test_create_incident_adds_timeline_event() -> None:
    db = FakeSession()
    service = IncidentService(db)  # type: ignore[arg-type]
    request = IncidentCreate(
        title="Checkout latency",
        description="p95 crossed the threshold",
        severity=IncidentSeverity.high,
        dedupe_key="monitor:checkout:prod:latency",
    )

    incident = service.create_incident(uuid4(), request, actor_id=uuid4())

    assert incident.title == "Checkout latency"
    assert incident.status == IncidentStatus.open
    assert len(db.added) == 3
    assert db.commits == 1


def test_update_incident_without_changes_still_returns_incident(monkeypatch) -> None:
    db = FakeSession()
    service = IncidentService(db)  # type: ignore[arg-type]
    existing = SimpleNamespace(
        id=uuid4(),
        status=IncidentStatus.open,
        severity=IncidentSeverity.medium,
        assignee_id=None,
    )
    monkeypatch.setattr(service, "get_incident", lambda organization_id, incident_id: existing)

    updated = service.update_incident(
        uuid4(),
        uuid4(),
        IncidentUpdate(status=IncidentStatus.open),
        actor_id=uuid4(),
    )

    assert updated is existing
    assert db.commits == 1
    assert db.added == []

