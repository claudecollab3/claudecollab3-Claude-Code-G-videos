// Same-origin "/api/v1" works when a reverse proxy (Vite dev, or
// docker/nginx.conf in production) sits in front of both frontend and
// backend. When they're deployed as separate services with different
// origins (e.g. a Render static site + a Render web service), set
// VITE_API_BASE_URL to the backend's full URL at build time instead.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export function websocketUrl(path: string): string {
  if (import.meta.env.VITE_API_BASE_URL) {
    const base = new URL(import.meta.env.VITE_API_BASE_URL);
    const protocol = base.protocol === "https:" ? "wss" : "ws";
    return `${protocol}://${base.host}${path}`;
  }
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  return `${protocol}://${window.location.host}${path}`;
}

let accessToken: string | null = localStorage.getItem("access_token");
let refreshToken: string | null = localStorage.getItem("refresh_token");

export function getAccessToken(): string | null {
  return accessToken;
}

export function setTokens(access: string | null, refresh: string | null): void {
  accessToken = access;
  refreshToken = refresh;
  if (access) localStorage.setItem("access_token", access);
  else localStorage.removeItem("access_token");
  if (refresh) localStorage.setItem("refresh_token", refresh);
  else localStorage.removeItem("refresh_token");
}

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshToken) return false;
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) {
    setTokens(null, null);
    return false;
  }
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return true;
}

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  let res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401 && refreshToken && path !== "/auth/refresh") {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers.set("Authorization", `Bearer ${accessToken}`);
      res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    }
  }

  return res;
}

export async function apiJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, options);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      /* response wasn't JSON; fall back to statusText */
    }
    throw new Error(`${res.status} ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}
