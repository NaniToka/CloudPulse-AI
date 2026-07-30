import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { serviceErrors, costByService, deployments } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import { CheckCircle2, XCircle, Loader2, GitCommit } from "lucide-react";

// ── Top Services by Error Rate ────────────────────────────────────────────────
function ErrorRateCard() {
  const sorted = [...serviceErrors].sort((a, b) => b.errorRate - a.errorRate);
  const max = sorted[0].errorRate;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-foreground text-sm font-semibold">
          Top Services by Error Rate
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {sorted.map((svc) => (
          <div key={svc.name} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono text-foreground/80">{svc.name}</span>
              <div className="flex items-center gap-2 text-muted-foreground">
                <span>{svc.requests.toLocaleString()} req/h</span>
                <span
                  className={cn(
                    "font-bold tabular-nums",
                    svc.errorRate > 0.5 ? "text-danger" :
                    svc.errorRate > 0.2 ? "text-warning" : "text-success"
                  )}
                >
                  {svc.errorRate.toFixed(2)}%
                </span>
              </div>
            </div>
            <div className="h-1.5 w-full rounded-full bg-bg-overlay overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  svc.errorRate > 0.5 ? "bg-danger" :
                  svc.errorRate > 0.2 ? "bg-warning" : "bg-success"
                )}
                style={{ width: `${(svc.errorRate / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ── Cost by Service Donut ─────────────────────────────────────────────────────
function CostDonutTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const { name, value } = payload[0].payload;
  return (
    <div className="glass rounded-lg border border-white/10 px-3 py-2 text-xs shadow-lg">
      <p className="font-semibold text-foreground">{name}</p>
      <p className="text-muted-foreground">${value.toLocaleString()}/mo</p>
    </div>
  );
}

function CostDonutCard() {
  const total = costByService.reduce((s, c) => s + c.value, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-foreground text-sm font-semibold">Cost by Service</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="relative">
            <ResponsiveContainer width={120} height={120}>
              <PieChart>
                <Pie
                  data={costByService}
                  cx="50%"
                  cy="50%"
                  innerRadius={36}
                  outerRadius={52}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {costByService.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<CostDonutTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <p className="text-[10px] text-muted-foreground">Total</p>
              <p className="text-sm font-bold gradient-text">${(total / 1000).toFixed(0)}k</p>
            </div>
          </div>

          <div className="flex-1 space-y-2">
            {costByService.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="h-2 w-2 rounded-full shrink-0" style={{ background: item.fill }} />
                  <span className="text-muted-foreground">{item.name}</span>
                </div>
                <span className="font-medium text-foreground tabular-nums">
                  {((item.value / total) * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Deployment Activity ───────────────────────────────────────────────────────
function DeploymentsCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-foreground text-sm font-semibold">Deployment Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative pl-5 space-y-4">
          {/* Vertical timeline line */}
          <div className="absolute left-[9px] top-1 bottom-1 w-[1px] bg-white/[0.08]" />

          {deployments.map((dep, i) => (
            <div key={i} className="relative flex items-start gap-3">
              {/* Dot */}
              <div className={cn(
                "absolute -left-5 mt-[3px] flex h-4 w-4 items-center justify-center rounded-full bg-bg-void ring-2",
                dep.status === "success" ? "ring-success/40" :
                dep.status === "failed" ? "ring-danger/40" : "ring-brand-blue/40"
              )}>
                {dep.status === "success" ? (
                  <CheckCircle2 className="h-3 w-3 text-success" />
                ) : dep.status === "failed" ? (
                  <XCircle className="h-3 w-3 text-danger" />
                ) : (
                  <Loader2 className="h-3 w-3 text-brand-blue animate-spin" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between gap-2">
                  <p className="text-sm font-medium text-foreground truncate">{dep.service}</p>
                  <span className="text-[10px] text-muted-foreground shrink-0">{dep.time}</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <GitCommit className="h-3 w-3 text-muted-foreground/50" />
                  <span className="text-xs font-mono text-muted-foreground">{dep.version}</span>
                  <span className="flex h-4 w-4 items-center justify-center rounded-full bg-brand-gradient text-[9px] font-bold text-white">
                    {dep.deployer}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function BottomRow() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      <ErrorRateCard />
      <CostDonutCard />
      <DeploymentsCard />
    </div>
  );
}
