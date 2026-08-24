"use client";

import { useEffect, useState } from "react";
import { AppShell } from "./components/AppShell";
import { apiGet, ApiError } from "./lib/api";
import { getOrganization, getToken } from "./lib/session";
import type { DashboardSummary, Incident } from "./lib/types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [queue, setQueue] = useState<Incident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    async function load() {
      try {
        const [summaryData, incidents] = await Promise.all([
          apiGet<DashboardSummary>(`/organizations/${organization!.organization_id}/dashboard/summary`, token!),
          apiGet<Incident[]>(`/organizations/${organization!.organization_id}/incidents?status=open&limit=5`, token!)
        ]);
        setSummary(summaryData);
        setQueue(incidents);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Unable to load dashboard data.");
      }
    }

    load();
  }, []);

  const stats = [
    { label: "Open incidents", value: summary?.open_incidents ?? "-" },
    { label: "Alerts processed", value: summary?.alerts_processed ?? "-" },
    { label: "Workflow runs", value: summary?.workflow_runs ?? "-" }
  ];

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Operations overview</h1>
          <p>Monitor incidents, alert flow, and automation health.</p>
        </div>
      </div>
      {error && <p className="hint error-text">{error}</p>}
      <div className="grid grid-four">
        {stats.map((item) => (
          <article className="card" key={item.label}>
            <div className="stat">{item.label}</div>
            <div className="value">{item.value}</div>
          </article>
        ))}
      </div>
      <article className="card section-card">
        <h2>Response queue</h2>
        <div className="stack">
          {queue.length === 0 && <p className="hint">No open incidents.</p>}
          {queue.map((incident) => (
            <div className="queue-row" key={incident.id}>
              <span>{incident.title}</span>
              <a href="/incidents">Review</a>
            </div>
          ))}
        </div>
      </article>
    </AppShell>
  );
}
