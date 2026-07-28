from uuid import uuid4

from app.services.dashboard_service import DashboardService


class EmptySession:
    def scalar(self, statement):
        return 0


def test_dashboard_summary_defaults_to_zero_counts() -> None:
    service = DashboardService(EmptySession())  # type: ignore[arg-type]

    summary = service.organization_summary(uuid4())

    assert summary == {"open_incidents": 0, "alerts_processed": 0, "workflow_runs": 0}
