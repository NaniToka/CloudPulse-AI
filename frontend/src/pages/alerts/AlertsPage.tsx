import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import { alerts } from "@/lib/mockData";
import { AlertTriangle } from "lucide-react";

export default function AlertsPage() {
  const active       = alerts.filter((a) => a.status === "active").length;
  const acknowledged = alerts.filter((a) => a.status === "acknowledged").length;
  const resolved     = alerts.filter((a) => a.status === "resolved").length;
  const critical     = alerts.filter((a) => a.severity === "critical").length;

  return (
    <div className="space-y-6">
      <PageHeader title="Alerts" subtitle="All active and recent alert events" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Active"       value={active}       icon={<AlertTriangle className="h-4 w-4" />} />
        <StatCard label="Critical"     value={critical}     />
        <StatCard label="Acknowledged" value={acknowledged} />
        <StatCard label="Resolved"     value={resolved}     trend={{ value: "today", direction: "up", positive: true }} />
      </div>
      <AlertsPanel />
    </div>
  );
}
