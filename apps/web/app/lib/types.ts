export type Severity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "open" | "acknowledged" | "mitigated" | "resolved" | "archived";

export type Incident = {
  id: string;
  title: string;
  description?: string;
  severity: Severity;
  status: IncidentStatus;
  assignee_id?: string;
  created_at: string;
  updated_at: string;
};

export type DashboardSummary = {
  open_incidents: number;
  alerts_processed: number;
  workflow_runs: number;
};
