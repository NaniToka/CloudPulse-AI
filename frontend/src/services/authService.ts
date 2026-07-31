/**
 * Auth service — thin wrappers around the FastAPI auth endpoints.
 *
 * Error shape from the backend:
 *   { "error": "Human-readable message", "details": [...] }   (4xx)
 *
 * Axios throws on non-2xx; callers receive an AxiosError whose
 * response.data matches the shape above.
 */

import apiClient from "@/lib/api";
import type { LoginRequest, RegisterRequest, TokenResponse } from "@/types/auth";
import type { User, UserProfile } from "@/types/user";

export const authService = {
  /**
   * POST /api/v1/auth/login
   * Returns access + refresh tokens.
   */
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>("/auth/login", data);
    return response.data;
  },

  /**
   * POST /api/v1/auth/register
   * Creates a user (+ optional org) and returns tokens.
   */
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>("/auth/register", data);
    return response.data;
  },

  /**
   * GET /api/v1/auth/me
   * Returns the currently authenticated user.
   * The Authorization header is injected automatically by the Axios interceptor.
   */
  async getMe(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  /**
   * GET /api/v1/users/me
   * Returns extended profile including organization_name.
   */
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>("/users/me");
    return response.data;
  },

  /**
   * POST /api/v1/auth/logout
   * Server is stateless — this call just lets the backend log the event.
   * The client clears tokens regardless of outcome (handled in useLogout).
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Ignore — we clear tokens on the client regardless
    }
  },

  /**
   * POST /api/v1/auth/refresh
   * Exchange a refresh token for a new access token.
   * Called automatically by the Axios interceptor; exposed here for manual use.
   */
  async refresh(refreshToken: string): Promise<{ access_token: string; expires_in: number }> {
    const response = await apiClient.post("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};

/**
 * Extract a human-readable error message from an Axios error.
 * The backend always returns { "error": "...", "details": [...] }.
 */
export function getApiErrorMessage(error: unknown, fallback = "An unexpected error occurred."): string {
  if (!error || typeof error !== "object") return fallback;
  const axiosErr = error as { response?: { data?: { error?: string; detail?: string } } };
  return (
    axiosErr.response?.data?.error ??
    axiosErr.response?.data?.detail ??
    fallback
  );
}
