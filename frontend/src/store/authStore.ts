/**
 * Zustand auth store.
 *
 * Responsibilities
 * ----------------
 * - Persists { accessToken, refreshToken, isAuthenticated, user } to
 *   localStorage under the key "cloudpulse-auth" via the persist middleware.
 * - On hydration (page reload) the onRehydrateStorage callback re-syncs the
 *   individual "access_token" / "refresh_token" localStorage keys that the
 *   Axios interceptor reads directly.  This guarantees both storage locations
 *   stay in sync without any extra effect in the app.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types/user";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  /** Store both tokens and mark the session as authenticated. */
  setTokens: (access: string, refresh: string) => void;

  /** Update the in-memory user object (called after /auth/me). */
  setUser: (user: User) => void;

  /** Clear all auth state — used by useLogout and the Axios 401 handler. */
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setTokens: (access, refresh) => {
        // Write to the flat keys so the Axios interceptor finds them
        localStorage.setItem("access_token", access);
        localStorage.setItem("refresh_token", refresh);
        set({ accessToken: access, refreshToken: refresh, isAuthenticated: true });
      },

      setUser: (user) => set({ user }),

      logout: () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: "cloudpulse-auth",

      // Only persist what's needed — avoids stale data issues
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        user: state.user,
      }),

      // Re-sync flat localStorage keys when the persisted state is rehydrated
      onRehydrateStorage: () => (state) => {
        if (state?.accessToken) {
          localStorage.setItem("access_token", state.accessToken);
        }
        if (state?.refreshToken) {
          localStorage.setItem("refresh_token", state.refreshToken);
        }
      },
    }
  )
);
