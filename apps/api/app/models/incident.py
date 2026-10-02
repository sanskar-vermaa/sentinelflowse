from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class IncidentSeverity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(StrEnum):
    open = "open"
    acknowledged = "acknowledged"
    mitigated = "mitigated"
    resolved = "resolved"
    archived = "archived"


class Incident(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity), index=True)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus), default=IncidentStatus.open, index=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    dedupe_key: Mapped[str] = mapped_column(String(128), index=True)


class IncidentTimelineEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incident_timeline_events"

    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    body: Mapped[str] = mapped_column(Text)
