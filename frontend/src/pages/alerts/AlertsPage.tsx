import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import { useAlertsQuery } from "@/hooks/useDashboardQuery";
import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";

export default function AlertsPage() {
  const { data: alerts = [] } = useAlertsQuery();

  const active = alerts.filter((a) => a.status === "active").length;
  const acknowledged = alerts.filter((a) => a.status === "acknowledged").length;
  const resolved = alerts.filter((a) => a.status === "resolved").length;
  const critical = alerts.filter((a) => a.severity === "critical").length;

  return (
    <div className="space-y-6">
      <PageHeader title="Alerts" subtitle="All active and recent infrastructure alert events" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Active" value={active} icon={<AlertTriangle className="h-4 w-4 text-rose-400" />} />
        <StatCard label="Critical" value={critical} icon={<ShieldAlert className="h-4 w-4 text-rose-500" />} />
        <StatCard label="Acknowledged" value={acknowledged} icon={<AlertTriangle className="h-4 w-4 text-amber-400" />} />
        <StatCard
          label="Resolved"
          value={resolved}
          icon={<CheckCircle2 className="h-4 w-4 text-emerald-400" />}
          trend={{ value: "today", direction: "up", positive: true }}
        />
      </div>
      <AlertsPanel />
    </div>
  );
}
