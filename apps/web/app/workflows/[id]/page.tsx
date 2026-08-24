"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/AppShell";
import { Badge } from "../../components/Badge";
import { apiGet, ApiError } from "../../lib/api";
import { getOrganization, getToken } from "../../lib/session";
import type { Workflow, WorkflowRun } from "../../lib/types";

export default function WorkflowDetailPage({ params }: { params: { id: string } }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    const base = `/organizations/${organization.organization_id}/workflows/${params.id}`;
    Promise.all([apiGet<Workflow>(base, token), apiGet<WorkflowRun[]>(`${base}/runs`, token)])
      .then(([workflowData, runsData]) => {
        setWorkflow(workflowData);
        setRuns(runsData);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load workflow."));
  }, [params.id]);

  if (error) {
    return (
      <AppShell>
        <p className="hint error-text">{error}</p>
      </AppShell>
    );
  }

  if (!workflow) {
    return <AppShell><p className="hint">Loading...</p></AppShell>;
  }

  const steps = workflow.definition.steps ?? [];

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>{workflow.name}</h1>
          <p>Trigger: {workflow.trigger}</p>
        </div>
        <Badge tone={workflow.is_enabled ? "success" : "neutral"}>{workflow.is_enabled ? "enabled" : "paused"}</Badge>
      </div>
      <article className="card">
        <h2>Steps</h2>
        <div className="stack">
          {steps.length === 0 && <p className="hint">No steps defined.</p>}
          {steps.map((step, index) => (
            <div className="queue-row" key={`${step.type}-${index}`}>
              <span>{index + 1}. {step.type}{step.channel ? ` (${step.channel})` : ""}</span>
            </div>
          ))}
        </div>
      </article>
      <article className="card section-card">
        <h2>Run history</h2>
        <div className="stack">
          {runs.length === 0 && <p className="hint">No runs yet.</p>}
          {runs.map((run) => (
            <div className="queue-row" key={run.id}>
              <span>{run.incident_id ?? "Manual run"}</span>
              <Badge tone={run.status === "succeeded" ? "success" : run.status === "failed" ? "danger" : "warning"}>
                {run.status}
              </Badge>
            </div>
          ))}
        </div>
      </article>
    </AppShell>
  );
}
