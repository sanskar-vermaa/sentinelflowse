"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, ApiError } from "../lib/api";
import { saveSession } from "../lib/session";
import type { Me, TokenResponse } from "../lib/types";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@sentinelflow.dev");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const token = await apiPost<TokenResponse>("/auth/login", { email, password });
      const me = await apiGet<Me>("/auth/me", token.access_token);
      const membership = me.memberships[0];
      if (!membership) {
        throw new Error("Your account is not a member of any organization yet.");
      }
      saveSession(token.access_token, token.refresh_token, membership, me.display_name);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to sign in. Check the API is running.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div>
          <h1>SentinelFlow</h1>
          <p>Sign in to triage incidents, review alerts, and manage response workflows.</p>
        </div>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              placeholder="ops@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              placeholder="••••••••••"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error && <p className="hint" style={{ color: "var(--danger)" }}>{error}</p>}
          <button type="submit" disabled={submitting}>
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="hint">Demo: admin@sentinelflow.dev / sentinelflow-demo</p>
      </section>
    </main>
  );
}
