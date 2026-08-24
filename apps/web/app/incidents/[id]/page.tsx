"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../components/AppShell";
import { Badge } from "../../components/Badge";
import { apiGet, ApiError } from "../../lib/api";
import { getOrganization, getToken } from "../../lib/session";
import type { Incident, IncidentTimelineEvent } from "../../lib/types";

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [timeline, setTimeline] = useState<IncidentTimelineEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    const base = `/organizations/${organization.organization_id}/incidents/${params.id}`;
    Promise.all([apiGet<Incident>(base, token), apiGet<IncidentTimelineEvent[]>(`${base}/timeline`, token)])
      .then(([incidentData, timelineData]) => {
        setIncident(incidentData);
        setTimeline(timelineData);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load incident."));
  }, [params.id]);

  if (error) {
    return (
      <AppShell>
        <p className="hint error-text">{error}</p>
      </AppShell>
    );
  }

  if (!incident) {
    return <AppShell><p className="hint">Loading...</p></AppShell>;
  }

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>{incident.title}</h1>
          <p>{incident.id}</p>
        </div>
        <Badge tone={incident.severity === "high" || incident.severity === "critical" ? "danger" : "neutral"}>
          {incident.severity}
        </Badge>
      </div>
      <div className="detail-grid">
        <article className="card">
          <h2>Summary</h2>
          <p>{incident.description ?? "No description provided."}</p>
          <div className="meta-row"><span>Status</span><Badge tone="warning">{incident.status}</Badge></div>
          <div className="meta-row"><span>Created</span><strong>{new Date(incident.created_at).toLocaleString()}</strong></div>
          <div className="meta-row"><span>Updated</span><strong>{new Date(incident.updated_at).toLocaleString()}</strong></div>
        </article>
        <article className="card">
          <h2>Timeline</h2>
          <div className="stack">
            {timeline.length === 0 && <p className="hint">No timeline events yet.</p>}
            {timeline.map((event) => (
              <div className="timeline-item" key={event.id}>{event.body}</div>
            ))}
          </div>
        </article>
      </div>
    </AppShell>
  );
}
