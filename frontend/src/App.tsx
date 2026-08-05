import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";

// Layouts
import AuthLayout from "@/layouts/AuthLayout";
import DashboardLayout from "@/layouts/DashboardLayout";

// Guards
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import GuestRoute from "@/components/auth/GuestRoute";

// Auth pages
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";

// Dashboard pages
import DashboardPage from "@/pages/dashboard/DashboardPage";
import AiCopilotPage from "@/pages/ai/AiCopilotPage";
import InfrastructurePage from "@/pages/infrastructure/InfrastructurePage";
import ServersPage from "@/pages/servers/ServersPage";
import LogsPage from "@/pages/logs/LogsPage";
import CostPage from "@/pages/cost/CostPage";
import IncidentsPage from "@/pages/incidents/IncidentsPage";
import PredictiveAnalyticsPage from "@/pages/predictions/PredictiveAnalyticsPage";
import RealTimeMonitoringPage from "@/pages/monitoring/RealTimeMonitoringPage";
import DistributedTracingPage from "@/pages/tracing/DistributedTracingPage";
import RAGChatPage from "@/pages/ragChat/RAGChatPage";
import RunbookDashboardPage from "@/pages/runbooks/RunbookDashboardPage";
import SecurityCenterPage from "@/pages/security/SecurityCenterPage";
import AlertsPage from "@/pages/alerts/AlertsPage";
import NotificationsPage from "@/pages/notifications/NotificationsPage";
import SettingsPage from "@/pages/settings/SettingsPage";

export default function App() {
  return (
    <>
      <Routes>
        {/* ── Public auth routes ────────────────────────────────── */}
        <Route element={<GuestRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login"    element={<LoginPage />}    />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
        </Route>

        {/* ── Protected app routes ──────────────────────────────── */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard"     element={<DashboardPage />}      />
            <Route path="/chat"          element={<RAGChatPage />}        />
            <Route path="/monitoring"    element={<RealTimeMonitoringPage />} />
            <Route path="/tracing"       element={<DistributedTracingPage />} />
            <Route path="/security"      element={<SecurityCenterPage />} />
            <Route path="/ai"            element={<AiCopilotPage />}      />
            <Route path="/infrastructure"element={<InfrastructurePage />} />
            <Route path="/servers"       element={<ServersPage />}        />
            <Route path="/logs"          element={<LogsPage />}           />
            <Route path="/cost"          element={<CostPage />}           />
            <Route path="/incidents"     element={<IncidentsPage />}      />
            <Route path="/runbooks"      element={<RunbookDashboardPage />} />
            <Route path="/predictions"   element={<PredictiveAnalyticsPage />} />
            <Route path="/alerts"        element={<AlertsPage />}         />
            <Route path="/notifications" element={<NotificationsPage />}  />
            <Route path="/settings"      element={<SettingsPage />}       />
          </Route>
        </Route>

        {/* ── Default redirects ─────────────────────────────────── */}
        <Route path="/"   element={<Navigate to="/dashboard" replace />} />
        <Route path="*"   element={<Navigate to="/dashboard" replace />} />
      </Routes>

      <Toaster />
    </>
  );
}
