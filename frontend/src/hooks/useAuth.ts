/**
 * React Query + Zustand hooks for authentication.
 *
 * useLogin      — POST /auth/login, stores tokens, fetches user, redirects
 * useRegister   — POST /auth/register, same flow as login
 * useLogout     — POST /auth/logout, clears everything, redirects
 * useCurrentUser — GET /auth/me, re-fetches the user on page load if a token exists
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService, getApiErrorMessage } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import { toast } from "@/hooks/useToast";
import type { LoginRequest, RegisterRequest } from "@/types/auth";

// ── Login ──────────────────────────────────────────────────────────────────

export function useLogin() {
  const { setTokens, setUser } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),

    onSuccess: async (tokens) => {
      // 1. Persist tokens (Axios interceptor will pick them up immediately)
      setTokens(tokens.access_token, tokens.refresh_token);

      // 2. Fetch the full user object from the backend
      try {
        const user = await authService.getMe();
        setUser(user);
      } catch {
        // Non-fatal — user info can be refreshed on the next page load
      }

      toast({
        title: "Welcome back!",
        description: "You have signed in successfully.",
        variant: "success",
      });

      navigate("/dashboard", { replace: true });
    },

    onError: (error) => {
      toast({
        title: "Sign in failed",
        description: getApiErrorMessage(error),
        variant: "destructive",
      });
    },
  });
}

// ── Register ───────────────────────────────────────────────────────────────

export function useRegister() {
  const { setTokens, setUser } = useAuthStore();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),

    onSuccess: async (tokens) => {
      setTokens(tokens.access_token, tokens.refresh_token);

      try {
        const user = await authService.getMe();
        setUser(user);
      } catch {
        // Non-fatal
      }

      toast({
        title: "Account created!",
        description: "Welcome to CloudPulse AI.",
        variant: "success",
      });

      navigate("/dashboard", { replace: true });
    },

    onError: (error) => {
      toast({
        title: "Registration failed",
        description: getApiErrorMessage(error),
        variant: "destructive",
      });
    },
  });
}

// ── Logout ─────────────────────────────────────────────────────────────────

export function useLogout() {
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authService.logout(),

    onSettled: () => {
      // Always clear state and redirect, regardless of server response
      logout();
      queryClient.clear();
      navigate("/login", { replace: true });
    },
  });
}

// ── Current user ───────────────────────────────────────────────────────────

export function useCurrentUser() {
  const { isAuthenticated, setUser } = useAuthStore();

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const user = await authService.getMe();
      setUser(user);          // keep Zustand store in sync
      return user;
    },
    enabled: isAuthenticated, // only run when a token exists in the store
    staleTime: 5 * 60 * 1000, // treat the user object as fresh for 5 min
    retry: false,              // don't retry on 401 — the interceptor handles it
  });
}
