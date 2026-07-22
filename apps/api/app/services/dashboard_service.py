from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.incident import Incident, IncidentStatus
from app.models.workflow import WorkflowRun


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def organization_summary(self, organization_id: UUID) -> dict[str, int]:
        open_incidents = self.db.scalar(
            select(func.count()).select_from(Incident).where(
                Incident.organization_id == str(organization_id),
                Incident.status.in_([IncidentStatus.open, IncidentStatus.acknowledged]),
            )
        )
        alerts = self.db.scalar(
            select(func.count()).select_from(Alert).where(Alert.organization_id == str(organization_id))
        )
        workflow_runs = self.db.scalar(select(func.count()).select_from(WorkflowRun))
        return {
            "open_incidents": int(open_incidents or 0),
            "alerts_processed": int(alerts or 0),
            "workflow_runs": int(workflow_runs or 0),
        }

