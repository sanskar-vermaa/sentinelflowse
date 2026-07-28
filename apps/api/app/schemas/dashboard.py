from pydantic import BaseModel


class DashboardSummary(BaseModel):
    open_incidents: int
    alerts_processed: int
    workflow_runs: int
