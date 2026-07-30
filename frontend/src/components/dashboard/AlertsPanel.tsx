import { Bell, ChevronRight, CheckCheck } from "lucide-react";
import { NavLink } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { alerts } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import type { Alert } from "@/types/dashboard";

const severityConfig: Record<Alert["severity"], {
  dot: string;
  badge: "danger" | "warning" | "muted" | "info";
  label: string;
}> = {
  critical: { dot: "bg-critical animate-pulse", badge: "danger",  label: "Critical" },
  high:     { dot: "bg-danger",                  badge: "danger",  label: "High"     },
  medium:   { dot: "bg-warning",                 badge: "warning", label: "Medium"   },
  low:      { dot: "bg-muted-foreground",        badge: "muted",   label: "Low"      },
};

const statusStyle: Record<Alert["status"], string> = {
  active:       "text-danger",
  acknowledged: "text-warning",
  resolved:     "text-success",
};

export default function AlertsPanel() {
  const active = alerts.filter((a) => a.status === "active").length;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-foreground text-sm font-semibold">Recent Alerts</CardTitle>
            {active > 0 && (
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-danger/20 px-1.5 text-[10px] font-bold text-danger border border-danger/30">
                {active}
              </span>
            )}
          </div>
          <NavLink
            to="/alerts"
            className="flex items-center gap-1 text-xs text-brand-blue hover:underline"
          >
            View all <ChevronRight className="h-3 w-3" />
          </NavLink>
        </div>
      </CardHeader>

      <CardContent className="px-2 pb-2">
        <div className="divide-y divide-white/[0.04]">
          {alerts.map((alert) => {
            const cfg = severityConfig[alert.severity];
            return (
              <div
                key={alert.id}
                className="flex items-start gap-3 rounded-lg px-3 py-3 hover:bg-white/[0.03] transition-colors group cursor-pointer"
              >
                <div className={cn("mt-1 h-2 w-2 rounded-full shrink-0", cfg.dot)} />
                <div className="flex-1 min-w-0 space-y-1">
                  <p className="text-xs font-medium text-foreground leading-snug">{alert.title}</p>
                  <div className="flex items-center gap-2 text-[10px]">
                    <span className="font-mono text-muted-foreground/70">{alert.service}</span>
                    <span className="text-muted-foreground/40">·</span>
                    <span className="text-muted-foreground">{alert.time}</span>
                    <span className="text-muted-foreground/40">·</span>
                    <span className={cn("font-medium capitalize", statusStyle[alert.status])}>
                      {alert.status}
                    </span>
                  </div>
                </div>
                <Badge variant={cfg.badge} className="shrink-0 text-[10px]">{cfg.label}</Badge>
              </div>
            );
          })}
        </div>

        <div className="px-3 pt-3">
          <Button variant="ghost" size="sm" className="w-full gap-2 text-xs text-muted-foreground hover:text-foreground">
            <CheckCheck className="h-3.5 w-3.5" />
            Acknowledge all active alerts
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
