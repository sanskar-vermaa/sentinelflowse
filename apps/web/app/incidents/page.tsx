"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../components/AppShell";
import { Badge } from "../components/Badge";
import { apiGet, ApiError } from "../lib/api";
import { getOrganization, getToken } from "../lib/session";
import type { Incident } from "../lib/types";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    apiGet<Incident[]>(`/organizations/${organization.organization_id}/incidents`, token)
      .then(setIncidents)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load incidents."));
  }, []);

  return (
    <AppShell>
      <div className="toolbar">
        <h1>Incidents</h1>
      </div>
      {error && <p className="hint error-text">{error}</p>}
      <article className="card">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((incident) => (
              <tr key={incident.id}>
                <td>{incident.id.slice(0, 8)}</td>
                <td><a href={`/incidents/${incident.id}`}>{incident.title}</a></td>
                <td>
                  <Badge tone={incident.severity === "high" || incident.severity === "critical" ? "danger" : "neutral"}>
                    {incident.severity}
                  </Badge>
                </td>
                <td><Badge tone="warning">{incident.status}</Badge></td>
              </tr>
            ))}
            {incidents.length === 0 && !error && (
              <tr>
                <td colSpan={4}>No incidents yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}
