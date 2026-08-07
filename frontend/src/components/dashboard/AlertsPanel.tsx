import { Bell, ChevronRight, CheckCheck, Loader2 } from "lucide-react";
import { NavLink } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAlertsQuery } from "@/hooks/useDashboardQuery";
import { cn } from "@/lib/utils";

const severityConfig: Record<string, { dot: string; badge: "danger" | "warning" | "muted" | "info"; label: string }> = {
  critical: { dot: "bg-rose-500 animate-pulse", badge: "danger", label: "Critical" },
  high: { dot: "bg-rose-500", badge: "danger", label: "High" },
  medium: { dot: "bg-amber-500", badge: "warning", label: "Medium" },
  low: { dot: "bg-slate-500", badge: "muted", label: "Low" },
};

const statusStyle: Record<string, string> = {
  active: "text-rose-400 font-semibold",
  acknowledged: "text-amber-400",
  resolved: "text-emerald-400",
};

export default function AlertsPanel() {
  const { data: alerts = [], isLoading, acknowledgeAllAlerts, acknowledgeAlert, resolveAlert } = useAlertsQuery();
  const activeCount = alerts.filter((a) => a.status === "active").length;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-foreground text-sm font-semibold">Recent Alerts</CardTitle>
            {activeCount > 0 && (
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500/20 px-1.5 text-[10px] font-bold text-rose-400 border border-rose-500/30">
                {activeCount}
              </span>
            )}
          </div>
          <NavLink to="/alerts" className="flex items-center gap-1 text-xs text-brand-blue hover:underline">
            View all <ChevronRight className="h-3 w-3" />
          </NavLink>
        </div>
      </CardHeader>

      <CardContent className="px-2 pb-2">
        {isLoading ? (
          <div className="flex h-36 items-center justify-center gap-2 text-muted-foreground text-xs">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading alerts...
          </div>
        ) : alerts.length === 0 ? (
          <div className="p-6 text-center text-muted-foreground text-xs">No active alerts. All systems operational.</div>
        ) : (
          <div className="divide-y divide-white/[0.04]">
            {alerts.slice(0, 6).map((alert) => {
              const cfg = severityConfig[alert.severity] || severityConfig.medium;
              return (
                <div
                  key={alert.id}
                  className="flex items-start gap-3 rounded-lg px-3 py-2.5 hover:bg-white/[0.03] transition-colors group"
                >
                  <div className={cn("mt-1 h-2 w-2 rounded-full shrink-0", cfg.dot)} />
                  <div className="flex-1 min-w-0 space-y-1">
                    <p className="text-xs font-medium text-foreground leading-snug">{alert.title}</p>
                    <div className="flex items-center gap-2 text-[10px]">
                      <span className="font-mono text-muted-foreground/70">{alert.metric_name || "system"}</span>
                      <span className="text-muted-foreground/40">·</span>
                      <span className="text-muted-foreground">
                        {new Date(alert.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                      <span className="text-muted-foreground/40">·</span>
                      <span className={cn("font-medium capitalize", statusStyle[alert.status] || "text-muted-foreground")}>
                        {alert.status}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={cfg.badge} className="shrink-0 text-[10px]">
                      {cfg.label}
                    </Badge>
                    {alert.status === "active" && (
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="h-6 text-[10px] px-2 text-amber-400 hover:bg-amber-500/10"
                      >
                        Ack
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {activeCount > 0 && (
          <div className="px-3 pt-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => acknowledgeAllAlerts()}
              className="w-full gap-2 text-xs text-muted-foreground hover:text-foreground"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              Acknowledge all active alerts ({activeCount})
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
