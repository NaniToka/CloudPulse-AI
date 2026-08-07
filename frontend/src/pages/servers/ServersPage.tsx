import { useState } from "react";
import { RefreshCw, Server, CheckCircle2, AlertTriangle, XCircle, Plus, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useServersQuery } from "@/hooks/useDashboardQuery";
import { serverService } from "@/services/serverService";
import { useQueryClient } from "@tanstack/react-query";
import { cn } from "@/lib/utils";

const statusBadge: Record<string, "success" | "warning" | "danger" | "secondary"> = {
  healthy: "success",
  degraded: "warning",
  critical: "danger",
  down: "danger",
  offline: "secondary",
};

const providerColor: Record<string, string> = {
  AWS: "text-warning",
  GCP: "text-brand-blue",
  Azure: "text-brand-purple",
  "on-prem": "text-muted-foreground",
};

export default function ServersPage() {
  const [search, setSearch] = useState("");
  const [provider, setProvider] = useState("all");
  const queryClient = useQueryClient();

  const { data: servers = [], isLoading, refetch, isRefetching } = useServersQuery({
    search: search || undefined,
    provider: provider === "all" ? undefined : provider,
  });

  const healthy = servers.filter((s) => s.status === "healthy").length;
  const degraded = servers.filter((s) => s.status === "degraded").length;
  const down = servers.filter((s) => s.status === "down" || s.status === "offline" || s.status === "critical").length;

  const handleAddServer = async () => {
    const name = prompt("Enter Server Name (e.g. k8s-worker-01):");
    if (!name) return;
    try {
      await serverService.createServer({
        name,
        provider: "AWS",
        environment: "production",
        server_type: "container",
      });
      queryClient.invalidateQueries({ queryKey: ["servers"] });
    } catch (e) {
      alert("Failed to register server");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Servers"
        subtitle="All monitored compute resources & cloud instances"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isRefetching} className="gap-2">
              <RefreshCw className={cn("h-3.5 w-3.5", isRefetching && "animate-spin")} />
              Refresh
            </Button>
            <Button size="sm" onClick={handleAddServer} className="gap-2 bg-brand-blue hover:bg-brand-blue/90 text-white">
              <Plus className="h-3.5 w-3.5" />
              Register Server
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Total Servers" value={servers.length} icon={<Server className="h-4 w-4" />} />
        <StatCard
          label="Healthy"
          value={healthy}
          icon={<CheckCircle2 className="h-4 w-4 text-emerald-400" />}
          trend={{ value: `${healthy} running`, direction: "up", positive: true }}
        />
        <StatCard label="Degraded" value={degraded} icon={<AlertTriangle className="h-4 w-4 text-amber-400" />} />
        <StatCard label="Down / Critical" value={down} icon={<XCircle className="h-4 w-4 text-rose-400" />} />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
          <CardTitle className="text-foreground text-sm font-semibold">All Monitored Nodes</CardTitle>
          <div className="flex items-center gap-3">
            <Input
              placeholder="Filter by name or IP..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-48 text-xs"
            />
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="h-8 rounded-md border border-white/10 bg-background px-2 text-xs text-foreground"
            >
              <option value="all">All Providers</option>
              <option value="AWS">AWS</option>
              <option value="GCP">GCP</option>
              <option value="Azure">Azure</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-2 text-muted-foreground text-sm">
              <Loader2 className="h-5 w-5 animate-spin" /> Loading live servers...
            </div>
          ) : servers.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground text-sm">
              No server instances found. Click "Register Server" to add a node.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                    {["Name", "Type", "Provider", "Region", "IP Address", "Status", "CPU", "Memory", "Disk"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {servers.map((s) => {
                    const cpuVal = s.cpu_percent ?? 0;
                    const memVal = s.memory_percent ?? 0;
                    const diskVal = s.disk_percent ?? 0;
                    return (
                      <tr key={s.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3 font-mono text-xs font-medium text-foreground">{s.name}</td>
                        <td className="px-4 py-3 text-xs text-muted-foreground">{s.server_type}</td>
                        <td className={cn("px-4 py-3 text-xs font-semibold", providerColor[s.provider] || "text-foreground")}>
                          {s.provider}
                        </td>
                        <td className="px-4 py-3 text-xs text-muted-foreground font-mono">{s.region || "us-east-1"}</td>
                        <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{s.ip_address || "10.0.1.1"}</td>
                        <td className="px-4 py-3">
                          <Badge variant={statusBadge[s.status] || "secondary"}>{s.status}</Badge>
                        </td>
                        <td className="px-4 py-3 min-w-[100px]">
                          <div className="flex items-center gap-2">
                            <Progress
                              value={cpuVal}
                              className="h-1.5 w-16"
                              indicatorClassName={cpuVal > 85 ? "bg-rose-500" : "bg-sky-500"}
                            />
                            <span className="text-xs tabular-nums text-muted-foreground">{cpuVal.toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 min-w-[100px]">
                          <div className="flex items-center gap-2">
                            <Progress
                              value={memVal}
                              className="h-1.5 w-16"
                              indicatorClassName={memVal > 85 ? "bg-amber-500" : "bg-purple-500"}
                            />
                            <span className="text-xs tabular-nums text-muted-foreground">{memVal.toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{diskVal.toFixed(0)}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
