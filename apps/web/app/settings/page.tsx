"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../components/AppShell";
import { apiGet, apiPost, ApiError } from "../lib/api";
import { getOrganization, getToken } from "../lib/session";
import type { ApiKey } from "../lib/types";

export default function SettingsPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [name, setName] = useState("");
  const [newSecret, setNewSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  function load() {
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization) return;
    apiGet<ApiKey[]>(`/organizations/${organization.organization_id}/api-keys`, token)
      .then(setKeys)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Unable to load API keys."));
  }

  useEffect(load, []);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const token = getToken();
    const organization = getOrganization();
    if (!token || !organization || !name.trim()) return;

    setCreating(true);
    setError(null);
    try {
      const created = await apiPost<{ api_key: ApiKey; secret: string }>(
        `/organizations/${organization.organization_id}/api-keys`,
        { name: name.trim() },
        token
      );
      setNewSecret(created.secret);
      setName("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create API key.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <AppShell>
      <div className="toolbar">
        <div>
          <h1>Settings</h1>
          <p>Manage API keys and organization controls.</p>
        </div>
      </div>
      {error && <p className="hint error-text">{error}</p>}
      <article className="card">
        <h2>API keys</h2>
        <form className="inline-form" onSubmit={handleCreate}>
          <input
            placeholder="New key name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <button type="submit" disabled={creating}>{creating ? "Creating..." : "Create key"}</button>
        </form>
        {newSecret && (
          <p className="hint">
            New key secret (shown once): <strong>{newSecret}</strong>
          </p>
        )}
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Prefix</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {keys.map((key) => (
              <tr key={key.id}>
                <td>{key.name}</td>
                <td>{key.key_prefix}</td>
                <td>{key.revoked_at ? "Revoked" : "Active"}</td>
              </tr>
            ))}
            {keys.length === 0 && !error && (
              <tr>
                <td colSpan={3}>No API keys yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </article>
    </AppShell>
  );
}
