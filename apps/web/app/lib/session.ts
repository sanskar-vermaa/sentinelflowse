"use client";

import type { Membership } from "./types";

const TOKEN_KEY = "sentinelflow.access_token";
const ORG_KEY = "sentinelflow.organization";
const USER_KEY = "sentinelflow.display_name";

export type StoredOrganization = Pick<Membership, "organization_id" | "organization_name" | "role">;

export function saveSession(token: string, organization: StoredOrganization, displayName: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(ORG_KEY, JSON.stringify(organization));
  localStorage.setItem(USER_KEY, displayName);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getOrganization(): StoredOrganization | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(ORG_KEY);
  return raw ? (JSON.parse(raw) as StoredOrganization) : null;
}

export function getDisplayName(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(USER_KEY);
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(ORG_KEY);
  localStorage.removeItem(USER_KEY);
}
