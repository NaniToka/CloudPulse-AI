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
import { FinOpsGovernancePage } from "@/pages/cost/FinOpsGovernancePage";
import { ExecutiveCommandCenterPage } from "@/pages/executive/ExecutiveCommandCenterPage";
import { CommandCenterPage } from "@/pages/commandCenter/CommandCenterPage";
import { AutonomousOperationsPage } from "@/pages/autonomous/AutonomousOperationsPage";
import { SloIntelligencePage } from "@/pages/slo/SloIntelligencePage";
import { ServiceReliabilityPage } from "@/pages/reliability/ServiceReliabilityPage";
import IncidentsPage from "@/pages/incidents/IncidentsPage";
import PredictiveAnalyticsPage from "@/pages/predictions/PredictiveAnalyticsPage";
import RealTimeMonitoringPage from "@/pages/monitoring/RealTimeMonitoringPage";
import DistributedTracingPage from "@/pages/tracing/DistributedTracingPage";
import RAGChatPage from "@/pages/ragChat/RAGChatPage";
import RunbookDashboardPage from "@/pages/runbooks/RunbookDashboardPage";
import SecurityCenterPage from "@/pages/security/SecurityCenterPage";
import AIOpsCenterPage from "@/pages/aiops/AIOpsCenterPage";
import AlertsPage from "@/pages/alerts/AlertsPage";
import NotificationsPage from "@/pages/notifications/NotificationsPage";
import SettingsPage from "@/pages/settings/SettingsPage";
import OrganizationSettingsPage from "@/pages/tenant/OrganizationSettingsPage";
import MultiCloudDashboardPage from "@/pages/cloud/MultiCloudDashboardPage";
import CloudAccountsPage from "@/pages/cloud/CloudAccountsPage";
import CloudResourceExplorerPage from "@/pages/cloud/CloudResourceExplorerPage";
import KubernetesDashboardPage from "@/pages/kubernetes/KubernetesDashboardPage";
import K8sPodExplorerPage from "@/pages/kubernetes/K8sPodExplorerPage";
import K8sDeploymentExplorerPage from "@/pages/kubernetes/K8sDeploymentExplorerPage";
import WorkflowsListPage from "@/pages/workflows/WorkflowsListPage";
import WorkflowEditorPage from "@/pages/workflows/WorkflowEditorPage";
import DigitalTwinDashboardPage from "@/pages/twin/DigitalTwinDashboardPage";
import SimulationStudioPage from "@/pages/twin/SimulationStudioPage";

import TelemetryIntelligenceDashboardPage from "@/pages/telemetry/TelemetryIntelligenceDashboardPage";
import ServiceDependencyExplorerPage from "@/pages/dependencies/ServiceDependencyExplorerPage";
import SrePage from "@/pages/sre/SrePage";
import GovernancePage from "@/pages/governance/GovernancePage";

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
            <Route path="/dashboard"             element={<DashboardPage />}      />
            <Route path="/executive"             element={<ExecutiveCommandCenterPage />} />
            <Route path="/command-center"        element={<CommandCenterPage />} />
            <Route path="/autonomous"            element={<AutonomousOperationsPage />} />
            <Route path="/telemetry"             element={<TelemetryIntelligenceDashboardPage />} />
            <Route path="/twin"                  element={<DigitalTwinDashboardPage />} />
            <Route path="/twin/simulation/:id"   element={<SimulationStudioPage />} />
            <Route path="/workflows"             element={<WorkflowsListPage />}  />
            <Route path="/workflows/builder/:id" element={<WorkflowEditorPage />} />
            <Route path="/k8s"                   element={<KubernetesDashboardPage />} />
            <Route path="/k8s/pods"        element={<K8sPodExplorerPage />} />
            <Route path="/k8s/deployments" element={<K8sDeploymentExplorerPage />} />
            <Route path="/cloud"           element={<MultiCloudDashboardPage />} />
            <Route path="/cloud/accounts"  element={<CloudAccountsPage />} />
            <Route path="/cloud/resources" element={<CloudResourceExplorerPage />} />
            <Route path="/organization"    element={<OrganizationSettingsPage />} />
            <Route path="/aiops"         element={<AIOpsCenterPage />}    />
            <Route path="/chat"          element={<RAGChatPage />}        />
            <Route path="/monitoring"    element={<RealTimeMonitoringPage />} />
            <Route path="/tracing"       element={<DistributedTracingPage />} />
            <Route path="/security"      element={<SecurityCenterPage />} />
            <Route path="/ai"            element={<AiCopilotPage />}      />
            <Route path="/infrastructure"element={<InfrastructurePage />} />
            <Route path="/servers"       element={<ServersPage />}        />
            <Route path="/logs"          element={<LogsPage />}           />
            <Route path="/cost"          element={<CostPage />}           />
            <Route path="/finops/governance" element={<FinOpsGovernancePage />} />
            <Route path="/incidents"     element={<IncidentsPage />}      />
            <Route path="/sre"           element={<SrePage />}            />
            <Route path="/slo"           element={<SloIntelligencePage />} />
            <Route path="/reliability"   element={<ServiceReliabilityPage />} />
            <Route path="/governance"    element={<GovernancePage />}     />
            <Route path="/dependencies"  element={<ServiceDependencyExplorerPage />} />
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
