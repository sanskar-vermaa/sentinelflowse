"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell } from "../../components/AppShell";
import { Badge } from "../../components/Badge";
import { apiGet, apiPatch, apiPost, ApiError } from "../../lib/api";
import { getOrganization, getToken } from "../../lib/session";
import type { Alert, Incident, IncidentStatus, IncidentTimelineEvent, Triage } from "../../lib/types";

const NEXT_ACTIONS: Partial<Record<IncidentStatus, { label: string; status: IncidentStatus }[]>> = {
  open: [
    { label: "Acknowledge", status: "acknowledged" },
    { label: "Resolve", status: "resolved" }
  ],
  acknowledged: [
    { label: "Mark mitigated", status: "mitigated" },
    { label: "Resolve", status: "resolved" }
  ],
  mitigated: [{ label: "Resolve", status: "resolved" }],
  resolved: [{ label: "Reopen", status: "open" }]
};

function severityTone(severity: Incident["severity"]) {
  return severity === "high" || severity === "critical" ? "danger" : "neutral";
}

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [timeline, setTimeline] = useState<IncidentTimelineEvent[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [triage, setTriage] = useState<Triage | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const base = useCallback(() => {
    const organization = getOrganization();
    return organization ? `/organizations/${organization.organization_id}/incidents/${params.id}` : null;
  }, [params.id]);

  const load = useCallback(async () => {
    const token = getToken();
    const path = base();
    if (!token || !path) return;
    const [incidentData, timelineData, alertData] = await Promise.all([
      apiGet<Incident>(path, token),
      apiGet<IncidentTimelineEvent[]>(`${path}/timeline`, token),
      apiGet<Alert[]>(`${path}/alerts`, token)
    ]);
    setIncident(incidentData);
    setTimeline(timelineData);
    setAlerts(alertData);
  }, [base]);

  useEffect(() => {
    load().catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load incident."));
  }, [load]);

  async function run(label: string, action: () => Promise<void>) {
    setBusy(label);
    setError(null);
    try {
      await action();
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setBusy(null);
    }
  }

  function changeStatus(status: IncidentStatus, label: string) {
    const token = getToken();
    const path = base();
    if (!token || !path) return;
    return run(label, async () => {
      await apiPatch<Incident>(path, { status }, token);
    });
  }

  function requestTriage() {
    const token = getToken();
    const path = base();
    if (!token || !path) return;
    return run("triage", async () => {
      setTriage(await apiPost<Triage>(`${path}/triage`, {}, token));
    });
  }

  if (!incident) {
    return (
      <AppShell>
        <p className={error ? "hint error-text" : "hint"}>{error ?? "Loading..."}</p>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>{incident.title}</h1>
          <p>{incident.id}</p>
        </div>
        <Badge tone={severityTone(incident.severity)}>{incident.severity}</Badge>
      </div>

      {error && <p className="hint error-text" role="alert">{error}</p>}

      <div className="action-row">
        {(NEXT_ACTIONS[incident.status] ?? []).map((action) => (
          <button
            key={action.status}
            type="button"
            className="action-button"
            disabled={busy !== null}
            onClick={() => changeStatus(action.status, action.label)}
          >
            {busy === action.label ? "Saving..." : action.label}
          </button>
        ))}
        <button type="button" className="action-button primary" disabled={busy !== null} onClick={requestTriage}>
          {busy === "triage" ? "Analysing..." : "AI triage"}
        </button>
      </div>

      <div className="detail-grid">
        <div className="stack">
          <article className="card">
            <h2>Summary</h2>
            <p>{incident.description ?? "No description provided."}</p>
            <div className="meta-row"><span>Status</span><Badge tone="warning">{incident.status}</Badge></div>
            <div className="meta-row"><span>Created</span><strong>{new Date(incident.created_at).toLocaleString()}</strong></div>
            <div className="meta-row"><span>Updated</span><strong>{new Date(incident.updated_at).toLocaleString()}</strong></div>
            <div className="meta-row"><span>Grouped alerts</span><strong>{alerts.length}</strong></div>
          </article>

          {triage && (
            <article className="card" aria-live="polite">
              <h2>AI triage <span className="hint">({triage.provider})</span></h2>
              <p>{triage.summary}</p>
              <ol className="triage-list">
                {triage.recommended_actions.map((action) => (
                  <li key={action}>{action}</li>
                ))}
              </ol>
            </article>
          )}

          <article className="card">
            <h2>Alerts</h2>
            {alerts.length === 0 && <p className="hint">No alerts are linked to this incident.</p>}
            <div className="stack">
              {alerts.map((alert) => (
                <div className="meta-row" key={alert.id}>
                  <span>
                    <strong>{alert.source}</strong> · {alert.external_id}
                  </span>
                  <span className="hint">{new Date(alert.created_at).toLocaleString()}</span>
                </div>
              ))}
            </div>
          </article>
        </div>

        <article className="card">
          <h2>Timeline</h2>
          <div className="stack">
            {timeline.length === 0 && <p className="hint">No timeline events yet.</p>}
            {timeline.map((event) => (
              <div className="timeline-item" key={event.id}>
                <div className="timeline-meta">
                  {event.event_type} · {new Date(event.created_at).toLocaleString()}
                </div>
                <div className="timeline-body">{event.body}</div>
              </div>
            ))}
          </div>
        </article>
      </div>
    </AppShell>
  );
}
