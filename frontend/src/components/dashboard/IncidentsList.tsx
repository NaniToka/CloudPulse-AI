import { ArrowRight, AlertOctagon, AlertTriangle, Info, Bell } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { incidents } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import type { Incident } from "@/types/dashboard";

const severityConfig: Record<Incident["severity"], {
  icon: React.ElementType;
  badge: "danger" | "warning" | "info" | "muted";
  dot: string;
}> = {
  P0: { icon: AlertOctagon, badge: "danger", dot: "bg-critical" },
  P1: { icon: AlertOctagon, badge: "danger", dot: "bg-danger" },
  P2: { icon: AlertTriangle, badge: "warning", dot: "bg-warning" },
  P3: { icon: Info, badge: "info", dot: "bg-info" },
};

const statusConfig: Record<Incident["status"], string> = {
  Investigating: "text-warning",
  Mitigating: "text-brand-blue",
  Resolved: "text-success",
  Open: "text-muted-foreground",
};

function IncidentRow({ incident }: { incident: Incident }) {
  const cfg = severityConfig[incident.severity];
  const Icon = cfg.icon;

  return (
    <div className="flex items-start gap-3 rounded-lg px-3 py-3 hover:bg-bg-overlay transition-colors cursor-pointer group">
      {/* Severity icon */}
      <div className={cn("mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-bg-elevated border border-white/[0.06]")}>
        <Icon className={cn("h-3.5 w-3.5",
          incident.severity === "P0" || incident.severity === "P1" ? "text-danger" :
          incident.severity === "P2" ? "text-warning" : "text-muted-foreground"
        )} />
      </div>

      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant={cfg.badge}>{incident.severity}</Badge>
          <span className="text-xs font-mono text-muted-foreground/60">{incident.id}</span>
        </div>
        <p className="text-sm text-foreground font-medium leading-snug truncate">{incident.title}</p>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-muted-foreground font-mono">{incident.service}</span>
          <span className="text-muted-foreground/50">·</span>
          <span className="text-muted-foreground">{incident.timeAgo}</span>
          <span className="text-muted-foreground/50">·</span>
          <span className={cn("font-medium", statusConfig[incident.status])}>{incident.status}</span>
        </div>
      </div>

      <button className="shrink-0 text-xs text-brand-blue opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 hover:underline">
        AI Analysis <ArrowRight className="h-3 w-3" />
      </button>
    </div>
  );
}

export default function IncidentsList() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-foreground text-sm font-semibold">Recent Incidents</CardTitle>
          </div>
          <Button variant="ghost" size="sm" className="text-xs text-brand-blue hover:text-brand-purple gap-1">
            View all <ArrowRight className="h-3 w-3" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="px-2 pb-2">
        <div className="divide-y divide-white/[0.04]">
          {incidents.map((inc) => (
            <IncidentRow key={inc.id} incident={inc} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
