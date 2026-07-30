import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import StatusBar from "@/components/dashboard/StatusBar";
import KpiCards from "@/components/dashboard/KpiCards";
import SpendChart from "@/components/dashboard/SpendChart";
import IncidentsList from "@/components/dashboard/IncidentsList";
import AiInsightsPanel from "@/components/dashboard/AiInsightsPanel";
import BottomRow from "@/components/dashboard/BottomRow";
import { useAuthStore } from "@/store/authStore";
import { format } from "date-fns";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const now = new Date();

  return (
    <div className="space-y-6">
      {/* ── Page header ────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">
            Good {getTimeOfDay()},{" "}
            <span className="gradient-text">{user?.first_name ?? "Engineer"}</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {format(now, "EEEE, MMMM do, yyyy")} · Your infrastructure at a glance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline text-xs text-muted-foreground">
            Last updated 23s ago
          </span>
          <Button variant="outline" size="sm" className="gap-2">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* ── Status bar ─────────────────────────────────────────────────── */}
      <StatusBar />

      {/* ── KPI cards ──────────────────────────────────────────────────── */}
      <KpiCards />

      {/* ── Main grid: charts + AI panel ───────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {/* Left: spend chart + incidents */}
        <div className="xl:col-span-2 space-y-4">
          <SpendChart />
          <IncidentsList />
        </div>

        {/* Right: AI insights panel */}
        <div className="xl:col-span-1 min-h-0">
          <div className="sticky top-0">
            <AiInsightsPanel />
          </div>
        </div>
      </div>

      {/* ── Bottom row: error rates + cost donut + deployments ─────────── */}
      <BottomRow />
    </div>
  );
}

function getTimeOfDay(): string {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
