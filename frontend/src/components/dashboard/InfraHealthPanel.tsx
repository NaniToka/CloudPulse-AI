import { Server, Cloud, CheckCircle2, AlertTriangle, XCircle, ChevronRight } from "lucide-react";
import { NavLink } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { servers } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import type { Server as ServerType } from "@/types/dashboard";

const statusConfig = {
  healthy:  { icon: CheckCircle2, color: "text-success",  badge: "success"  as const, bar: "bg-success"  },
  degraded: { icon: AlertTriangle, color: "text-warning", badge: "warning"  as const, bar: "bg-warning"  },
  down:     { icon: XCircle,       color: "text-danger",  badge: "danger"   as const, bar: "bg-danger"   },
};

const providerColors: Record<string, string> = {
  AWS:   "text-warning",
  GCP:   "text-brand-blue",
  Azure: "text-brand-purple",
};

function ServerRow({ server }: { server: ServerType }) {
  const cfg = statusConfig[server.status];
  const Icon = cfg.icon;

  return (
    <div className="flex items-center gap-3 rounded-lg px-3 py-2.5 hover:bg-white/[0.03] transition-colors group cursor-pointer">
      <div className={cn("flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-bg-elevated border border-white/[0.06]")}>
        <Server className="h-3.5 w-3.5 text-muted-foreground" />
      </div>

      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <p className="text-xs font-medium text-foreground font-mono truncate">{server.name}</p>
            <span className={cn("text-[10px] font-semibold shrink-0", providerColors[server.provider])}>
              {server.provider}
            </span>
          </div>
          <Badge variant={cfg.badge} className="shrink-0 text-[10px]">{server.status}</Badge>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>CPU</span><span>{server.cpu}%</span>
            </div>
            <div className="h-1 w-full rounded-full bg-bg-overlay overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", cfg.bar)}
                style={{ width: `${server.cpu}%` }}
              />
            </div>
          </div>
          <div className="flex-1 space-y-0.5">
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>MEM</span><span>{server.memory}%</span>
            </div>
            <div className="h-1 w-full rounded-full bg-bg-overlay overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", server.memory > 80 ? "bg-warning" : "bg-brand-blue")}
                style={{ width: `${server.memory}%` }}
              />
            </div>
          </div>
          <span className="text-[10px] text-muted-foreground shrink-0 font-mono">{server.uptime}</span>
        </div>
      </div>
    </div>
  );
}

export default function InfraHealthPanel() {
  const healthy  = servers.filter((s) => s.status === "healthy").length;
  const degraded = servers.filter((s) => s.status === "degraded").length;
  const down     = servers.filter((s) => s.status === "down").length;

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cloud className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-foreground text-sm font-semibold">Infrastructure Health</CardTitle>
          </div>
          <NavLink
            to="/infrastructure"
            className="flex items-center gap-1 text-xs text-brand-blue hover:underline"
          >
            View all <ChevronRight className="h-3 w-3" />
          </NavLink>
        </div>

        {/* Summary pills */}
        <div className="flex gap-2 mt-2">
          <div className="flex items-center gap-1.5 rounded-md bg-success/10 border border-success/20 px-2.5 py-1 text-xs font-medium text-success">
            <CheckCircle2 className="h-3 w-3" />{healthy} healthy
          </div>
          <div className="flex items-center gap-1.5 rounded-md bg-warning/10 border border-warning/20 px-2.5 py-1 text-xs font-medium text-warning">
            <AlertTriangle className="h-3 w-3" />{degraded} degraded
          </div>
          <div className="flex items-center gap-1.5 rounded-md bg-danger/10 border border-danger/20 px-2.5 py-1 text-xs font-medium text-danger">
            <XCircle className="h-3 w-3" />{down} down
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 px-2 pb-2">
        <div className="divide-y divide-white/[0.04]">
          {servers.map((s) => <ServerRow key={s.id} server={s} />)}
        </div>
      </CardContent>
    </Card>
  );
}
