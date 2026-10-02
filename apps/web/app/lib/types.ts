export type Severity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "open" | "acknowledged" | "mitigated" | "resolved" | "archived";
export type MemberRole = "owner" | "admin" | "responder" | "viewer";
export type AlertSource = "webhook" | "github" | "monitor" | "ci";
export type WorkflowRunStatus = "queued" | "running" | "succeeded" | "failed" | "cancelled";

export type Incident = {
  id: string;
  title: string;
  description?: string | null;
  severity: Severity;
  status: IncidentStatus;
  assignee_id?: string | null;
  created_at: string;
  updated_at: string;
};

export type IncidentTimelineEvent = {
  id: string;
  incident_id: string;
  actor_id: string | null;
  event_type: string;
  body: string;
  created_at: string;
};

export type Alert = {
  id: string;
  source: AlertSource;
  external_id: string;
  title: string;
  fingerprint: string;
  summary: string | null;
  incident_id?: string | null;
  created_at: string;
};

export type Triage = {
  provider: string;
  summary: string;
  recommended_actions: string[];
};

export type Workflow = {
  id: string;
  name: string;
  trigger: string;
  definition: { steps?: { type: string; channel?: string }[] };
  is_enabled: boolean;
};

export type WorkflowRun = {
  id: string;
  workflow_id: string;
  incident_id: string | null;
  status: WorkflowRunStatus;
  output_payload: Record<string, unknown> | null;
};

export type AuditLog = {
  id: string;
  organization_id: string;
  actor_id: string | null;
  action: string;
  target_type: string;
  target_id: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type ApiKey = {
  id: string;
  name: string;
  key_prefix: string;
  last_used_at: string | null;
  revoked_at: string | null;
  created_at: string;
};

export type DashboardSummary = {
  open_incidents: number;
  alerts_processed: number;
  workflow_runs: number;
};

export type Membership = {
  organization_id: string;
  organization_name: string;
  role: MemberRole;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type Me = {
  id: string;
  email: string;
  display_name: string;
  memberships: Membership[];
};
