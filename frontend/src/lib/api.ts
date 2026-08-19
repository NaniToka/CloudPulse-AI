/**
 * Axios instance — single source of truth for all API calls.
 *
 * What this file does
 * -------------------
 * 1. Creates an axios instance pointed at VITE_API_BASE_URL (falls back to
 *    the Vite dev-server proxy path "/api/v1" so it works without a .env too).
 * 2. Request interceptor — attaches the JWT access token from localStorage to
 *    every outgoing request as "Authorization: Bearer <token>".
 * 3. Response interceptor — when a 401 is received:
 *    a. If no refresh token exists → clears auth state and redirects to /login.
 *    b. Calls POST /auth/refresh once.  While that request is in-flight, any
 *       other 401s are queued and replayed with the new token once it arrives.
 *    c. On refresh failure → clears auth and redirects to /login.
 */

import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/store/authStore";

// Vite exposes env variables on import.meta.env.  The tsconfig already
// includes "dom" so the type is correct — no cast needed.
const BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? "/api/v1"
).replace(/\/+$/, "");

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: false,
  timeout: 15_000, // 15 s — avoids hanging requests showing no feedback
});

// ── Helpers ──────────────────────────────────────────────────────────────────

function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

function getRefreshToken(): string | null {
  return localStorage.getItem("refresh_token");
}

function clearTokens(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("cloudpulse-auth");
  try {
    useAuthStore.getState().logout();
  } catch {
    // Ignore store initialization errors
  }
}

function setAccessToken(token: string): void {
  localStorage.setItem("access_token", token);
}

// ── Request interceptor: inject access token ──────────────────────────────

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: silent token refresh on 401 ─────────────────────

/**
 * Tracks whether a refresh call is already in-flight so we don't fire
 * multiple concurrent refresh requests.
 */
let isRefreshing = false;

/**
 * Requests that arrived while a refresh was in-flight are queued here.
 * Once the new token is available they are all retried.
 */
let pendingQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function flushQueue(error: unknown, token: string | null): void {
  pendingQueue.forEach(({ resolve, reject }) =>
    error ? reject(error) : resolve(token!)
  );
  pendingQueue = [];
}

apiClient.interceptors.response.use(
  (response) => response,

  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Only intercept 401s that haven't already been retried.
    // Also skip if the failing request IS the refresh call (avoids infinite loop).
    if (
      error.response?.status !== 401 ||
      original._retry ||
      original.url?.includes("/auth/refresh")
    ) {
      return Promise.reject(error);
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    // Queue this request while a refresh is in-flight.
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      })
        .then((newToken) => {
          original.headers!.Authorization = `Bearer ${newToken}`;
          return apiClient(original);
        })
        .catch((err) => Promise.reject(err));
    }

    original._retry = true;
    isRefreshing = true;

    try {
      const { data } = await axios.post<{
        access_token: string;
        expires_in: number;
      }>(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });

      const newToken = data.access_token;
      setAccessToken(newToken);
      flushQueue(null, newToken);

      original.headers!.Authorization = `Bearer ${newToken}`;
      return apiClient(original);
    } catch (refreshError) {
      flushQueue(refreshError, null);
      clearTokens();
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default apiClient;
