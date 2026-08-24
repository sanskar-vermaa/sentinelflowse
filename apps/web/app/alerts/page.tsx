"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../components/AppShell";
import { apiGet, ApiError } from "../lib/api";
import { getOrganization, getToken } from "../lib/session";
import type { Alert } from "../lib/types";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    apiGet<Alert[]>(`/organizations/${organization.organization_id}/alerts`, token)
      .then(setAlerts)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load alerts."));
  }, []);

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Alerts</h1>
          <p>Normalized events from monitors, CI, GitHub, and webhooks.</p>
        </div>
      </div>
      {error && <p className="hint error-text">{error}</p>}
      <article className="card">
        <table className="table">
          <thead>
            <tr><th>Source</th><th>Title</th><th>External ID</th><th>Received</th></tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.id}>
                <td>{alert.source}</td>
                <td>{alert.title}</td>
                <td>{alert.external_id}</td>
                <td>{new Date(alert.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {alerts.length === 0 && !error && (
              <tr>
                <td colSpan={4}>No alerts ingested yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}
