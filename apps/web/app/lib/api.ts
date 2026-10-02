import { clearSession, getRefreshToken, getToken, saveTokens } from "./session";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

let refreshing: Promise<string | null> | null = null;

// Exchanges the stored refresh token for new tokens. Concurrent 401s share
// one refresh call. Returns the new access token, or null if the session is over.
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;
  refreshing ??= fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store"
  })
    .then(async (res) => {
      if (!res.ok) return null;
      const tokens = (await res.json()) as { access_token: string; refresh_token: string };
      saveTokens(tokens.access_token, tokens.refresh_token);
      return tokens.access_token;
    })
    .catch(() => null)
    .finally(() => {
      refreshing = null;
    });
  return refreshing;
}

// FastAPI returns a string for most errors and a list of field errors for 422s.
function errorMessage(detail: unknown, status: number): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => (item && typeof item === "object" && "msg" in item ? String(item.msg) : ""));
    const joined = messages.filter(Boolean).join("; ");
    if (joined) return joined;
  }
  return `API request failed: ${status}`;
}

async function request<T>(path: string, options: RequestInit, token?: string, retried = false): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {})
    },
    cache: "no-store"
  });

  if (response.status === 401 && token && !retried && token === getToken()) {
    const fresh = await refreshAccessToken();
    if (fresh) return request<T>(path, options, fresh, true);
    clearSession();
    if (typeof window !== "undefined") window.location.assign("/login");
  }

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new ApiError(response.status, errorMessage(detail?.detail, response.status));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function apiGet<T>(path: string, token?: string): Promise<T> {
  return request<T>(path, { method: "GET" }, token);
}

export function apiPost<T>(path: string, body: unknown, token?: string): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) }, token);
}

export function apiPatch<T>(path: string, body: unknown, token?: string): Promise<T> {
  return request<T>(path, { method: "PATCH", body: JSON.stringify(body) }, token);
}
