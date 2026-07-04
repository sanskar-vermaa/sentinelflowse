export type IncidentSeverity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "open" | "acknowledged" | "mitigated" | "resolved" | "archived";

export interface IncidentSummary {
  id: string;
  title: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  assigneeId?: string;
  updatedAt: string;
}

export interface AlertIngestResult {
  alertId: string;
  accepted: boolean;
  dedupeKey: string;
  incidentId?: string;
}

