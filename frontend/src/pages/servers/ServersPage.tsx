import { RefreshCw, Server, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { servers } from "@/lib/mockData";
import { cn } from "@/lib/utils";

const statusBadge = { healthy: "success", degraded: "warning", down: "danger" } as const;
const providerColor: Record<string, string> = { AWS: "text-warning", GCP: "text-brand-blue", Azure: "text-brand-purple" };

export default function ServersPage() {
  const healthy  = servers.filter((s) => s.status === "healthy").length;
  const degraded = servers.filter((s) => s.status === "degraded").length;
  const down     = servers.filter((s) => s.status === "down").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Servers"
        subtitle="All monitored compute resources"
        actions={
          <Button variant="outline" size="sm" className="gap-2">
            <RefreshCw className="h-3.5 w-3.5" />Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Total Servers" value={servers.length} icon={<Server className="h-4 w-4" />} />
        <StatCard label="Healthy"       value={healthy}         icon={<CheckCircle2 className="h-4 w-4" />} trend={{ value: `${healthy} running`, direction: "up", positive: true }} />
        <StatCard label="Degraded"      value={degraded}        icon={<AlertTriangle className="h-4 w-4" />} />
        <StatCard label="Down"          value={down}            icon={<XCircle className="h-4 w-4" />} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground text-sm font-semibold">All Servers</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                  {["Name","Type","Provider","Region","Status","CPU","Memory","Uptime"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {servers.map((s) => (
                  <tr key={s.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                    <td className="px-4 py-3 font-mono text-xs font-medium text-foreground">{s.name}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{s.type}</td>
                    <td className={cn("px-4 py-3 text-xs font-semibold", providerColor[s.provider])}>{s.provider}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground font-mono">{s.region}</td>
                    <td className="px-4 py-3"><Badge variant={statusBadge[s.status]}>{s.status}</Badge></td>
                    <td className="px-4 py-3 min-w-[100px]">
                      <div className="flex items-center gap-2">
                        <Progress value={s.cpu} className="h-1.5 w-16" indicatorClassName={s.cpu > 85 ? "bg-danger" : "bg-brand-blue"} />
                        <span className="text-xs tabular-nums text-muted-foreground">{s.cpu}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 min-w-[100px]">
                      <div className="flex items-center gap-2">
                        <Progress value={s.memory} className="h-1.5 w-16" indicatorClassName={s.memory > 85 ? "bg-warning" : "bg-brand-violet"} />
                        <span className="text-xs tabular-nums text-muted-foreground">{s.memory}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs font-mono text-success">{s.uptime}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
