from enum import StrEnum

from sqlalchemy import JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class AlertSource(StrEnum):
    webhook = "webhook"
    github = "github"
    monitor = "monitor"
    ci = "ci"


class Alert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    source: Mapped[AlertSource] = mapped_column(Enum(AlertSource), index=True)
    external_id: Mapped[str] = mapped_column(String(180), index=True)
    title: Mapped[str] = mapped_column(String(240))
    fingerprint: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(Text)
    # The incident this alert was grouped into.
    incident_id: Mapped[str | None] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"), index=True)

