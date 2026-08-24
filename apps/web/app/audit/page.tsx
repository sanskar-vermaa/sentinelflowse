"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../components/AppShell";
import { apiGet, ApiError } from "../lib/api";
import { getOrganization, getToken } from "../lib/session";
import type { AuditLog } from "../lib/types";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;

    apiGet<AuditLog[]>(`/organizations/${organization.organization_id}/audit-logs`, token)
      .then(setLogs)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load audit log."));
  }, []);

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Audit log</h1>
          <p>Trace important organization actions and response decisions.</p>
        </div>
      </div>
      {error && <p className="hint error-text">{error}</p>}
      <article className="card">
        <table className="table">
          <thead>
            <tr><th>Action</th><th>Target</th><th>When</th></tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{log.action}</td>
                <td>{log.target_type}{log.target_id ? ` · ${log.target_id.slice(0, 8)}` : ""}</td>
                <td>{new Date(log.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {logs.length === 0 && !error && (
              <tr>
                <td colSpan={3}>No audit events recorded yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}
