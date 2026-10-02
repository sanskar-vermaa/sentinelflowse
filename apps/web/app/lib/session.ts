"use client";

import type { Membership } from "./types";

const TOKEN_KEY = "sentinelflow.access_token";
const REFRESH_KEY = "sentinelflow.refresh_token";
const ORG_KEY = "sentinelflow.organization";
const USER_KEY = "sentinelflow.display_name";

export type StoredOrganization = Pick<Membership, "organization_id" | "organization_name" | "role">;

export function saveSession(
  token: string,
  refreshToken: string,
  organization: StoredOrganization,
  displayName: string
): void {
  saveTokens(token, refreshToken);
  localStorage.setItem(ORG_KEY, JSON.stringify(organization));
  localStorage.setItem(USER_KEY, displayName);
}

export function saveTokens(token: string, refreshToken: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getOrganization(): StoredOrganization | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(ORG_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredOrganization;
  } catch {
    return null;
  }
}

export function getDisplayName(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(USER_KEY);
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(ORG_KEY);
  localStorage.removeItem(USER_KEY);
}
