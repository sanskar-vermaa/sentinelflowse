from enum import StrEnum

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class WorkflowRunStatus(StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class Workflow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workflows"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    trigger: Mapped[str] = mapped_column(String(80), index=True)
    definition: Mapped[dict] = mapped_column(JSON)
    is_enabled: Mapped[bool] = mapped_column(default=True)


class WorkflowRun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workflow_runs"

    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    incident_id: Mapped[str | None] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"))
    status: Mapped[WorkflowRunStatus] = mapped_column(Enum(WorkflowRunStatus), default=WorkflowRunStatus.queued)
    input_payload: Mapped[dict] = mapped_column(JSON)
    output_payload: Mapped[dict | None] = mapped_column(JSON)

