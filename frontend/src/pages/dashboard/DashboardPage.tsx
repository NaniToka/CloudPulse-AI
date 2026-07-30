import { RefreshCw, Server, CheckCircle2, AlertTriangle, DollarSign, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import StatusBar from "@/components/dashboard/StatusBar";
import SpendChart from "@/components/dashboard/SpendChart";
import CpuChart from "@/components/dashboard/CpuChart";
import MemoryChart from "@/components/dashboard/MemoryChart";
import NetworkChart from "@/components/dashboard/NetworkChart";
import IncidentTimeline from "@/components/dashboard/IncidentTimeline";
import InfraHealthPanel from "@/components/dashboard/InfraHealthPanel";
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import AiWidget from "@/components/dashboard/AiWidget";
import QuickActions from "@/components/dashboard/QuickActions";
import IncidentsList from "@/components/dashboard/IncidentsList";
import { useAuthStore } from "@/store/authStore";
import { format } from "date-fns";

function getGreeting(): string {
  const h = new Date().getHours();
  return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const now = new Date();

  return (
    <div className="space-y-6">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <PageHeader
        title={`${getGreeting()}, ${user?.first_name ?? "Engineer"} 👋`}
        subtitle={`${format(now, "EEEE, MMMM do, yyyy")} · Infrastructure overview`}
        actions={
          <>
            <span className="hidden sm:inline text-xs text-muted-foreground">
              Last synced 23s ago
            </span>
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh
            </Button>
          </>
        }
      />

      {/* ── Status bar ─────────────────────────────────────────────────── */}
      <StatusBar />

      {/* ── KPI stat cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        <StatCard
          label="Active Servers"
          value="2,847"
          subValue="across 3 cloud providers"
          icon={<Server className="h-4 w-4" />}
          trend={{ value: "+12 this week", direction: "up", positive: true }}
        />
        <StatCard
          label="Healthy Resources"
          value="96.1%"
          subValue="2,731 of 2,847 healthy"
          icon={<CheckCircle2 className="h-4 w-4" />}
          trend={{ value: "↑ +0.3% from yesterday", direction: "up", positive: true }}
        />
        <StatCard
          label="Active Alerts"
          value="47"
          subValue="6 critical · 12 high"
          icon={<AlertTriangle className="h-4 w-4" />}
          trend={{ value: "↓ 12 from yesterday", direction: "down", positive: true }}
        />
        <StatCard
          label="Monthly Cost"
          value="$84,230"
          subValue="Forecast $102,400"
          icon={<DollarSign className="h-4 w-4" />}
          trend={{ value: "+3.2% vs last month", direction: "up", positive: false }}
        />
      </div>

      {/* ── Quick actions ───────────────────────────────────────────────── */}
      <QuickActions />

      {/* ── Charts tabs ────────────────────────────────────────────────── */}
      <Tabs defaultValue="cpu">
        <div className="flex items-center justify-between gap-4 mb-1">
          <h2 className="text-sm font-semibold text-foreground">Performance Metrics</h2>
          <TabsList>
            <TabsTrigger value="cpu">CPU</TabsTrigger>
            <TabsTrigger value="memory">Memory</TabsTrigger>
            <TabsTrigger value="network">Network</TabsTrigger>
            <TabsTrigger value="cost">Cost</TabsTrigger>
            <TabsTrigger value="incidents">Incidents</TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="cpu"><CpuChart /></TabsContent>
        <TabsContent value="memory"><MemoryChart /></TabsContent>
        <TabsContent value="network"><NetworkChart /></TabsContent>
        <TabsContent value="cost"><SpendChart /></TabsContent>
        <TabsContent value="incidents"><IncidentTimeline /></TabsContent>
      </Tabs>

      {/* ── Main 3-column grid ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {/* Infrastructure health — spans 2 cols on xl */}
        <div className="xl:col-span-2">
          <InfraHealthPanel />
        </div>

        {/* AI recommendations */}
        <div className="xl:col-span-1">
          <AiWidget />
        </div>
      </div>

      {/* ── Incidents + Alerts row ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <IncidentsList />
        <AlertsPanel />
      </div>
    </div>
  );
}
