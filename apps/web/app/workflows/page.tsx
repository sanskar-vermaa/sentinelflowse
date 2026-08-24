"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../components/AppShell";
import { apiGet, ApiError } from "../lib/api";
import { getOrganization, getToken } from "../lib/session";
import type { Workflow } from "../lib/types";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    apiGet<Workflow[]>(`/organizations/${organization.organization_id}/workflows`, token)
      .then(setWorkflows)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load workflows."));
  }, []);

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Workflows</h1>
          <p>Automate response steps with deterministic runbooks.</p>
        </div>
      </div>
      {error && <p className="hint error-text">{error}</p>}
      <div className="grid">
        {workflows.map((workflow) => (
          <article className="card" key={workflow.id}>
            <h2><a href={`/workflows/${workflow.id}`}>{workflow.name}</a></h2>
            <p>{workflow.trigger}</p>
            <strong>{workflow.is_enabled ? "Enabled" : "Paused"}</strong>
          </article>
        ))}
        {workflows.length === 0 && !error && <p className="hint">No workflows configured yet.</p>}
      </div>
    </AppShell>
  );
}
