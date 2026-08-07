import { useState } from "react";
import { Box, Search, RefreshCw, Terminal, AlertTriangle, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ContainerDetailsDrawer from "@/components/kubernetes/ContainerDetailsDrawer";
import { useK8sPods } from "@/hooks/useKubernetes";
import type { K8sPodItem } from "@/services/kubernetesService";
import { cn } from "@/lib/utils";

const statusBadgeVariant: Record<string, "success" | "warning" | "danger" | "secondary"> = {
  Running: "success",
  Pending: "warning",
  CrashLoopBackOff: "danger",
  OOMKilled: "danger",
  ImagePullBackOff: "danger",
};

export default function K8sPodExplorerPage() {
  const [search, setSearch] = useState("");
  const [namespace, setNamespace] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedPod, setSelectedPod] = useState<K8sPodItem | null>(null);

  const { data: pods = [], isLoading, refetch } = useK8sPods({
    search: search || undefined,
    namespace: namespace === "all" ? undefined : namespace,
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Pod & Container Explorer"
        subtitle="Real-time pod lifecycle, restart counters, container telemetry & log streams"
        actions={
          <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-2 text-xs">
            <RefreshCw className="h-3.5 w-3.5" /> Refresh Pods
          </Button>
        }
      />

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
          <CardTitle className="text-sm font-semibold text-foreground">Discovered Pods ({pods.length})</CardTitle>
          <div className="flex items-center gap-3">
            <Input
              placeholder="Search pod name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-56 text-xs"
            />
            <select
              value={namespace}
              onChange={(e) => setNamespace(e.target.value)}
              className="h-8 rounded-md border border-white/10 bg-background px-2 text-xs text-foreground"
            >
              <option value="all">All Namespaces</option>
              <option value="default">default</option>
              <option value="prod-billing">prod-billing</option>
              <option value="data-engine">data-engine</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-8 rounded-md border border-white/10 bg-background px-2 text-xs text-foreground"
            >
              <option value="all">All Statuses</option>
              <option value="Running">Running</option>
              <option value="CrashLoopBackOff">CrashLoopBackOff</option>
              <option value="OOMKilled">OOMKilled</option>
              <option value="Pending">Pending</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" /> Querying Kubernetes Pods...
            </div>
          ) : pods.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground">No pods match the selected filters.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                    {["Pod Name", "Namespace", "Deployment", "Status", "Restarts", "CPU Usage", "Memory Usage", "Actions"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {pods.map((p) => (
                    <tr
                      key={p.id}
                      onClick={() => setSelectedPod(p)}
                      className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3 font-mono text-xs font-semibold text-foreground">{p.name}</td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{p.namespace}</td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{p.deployment_name || "standalone"}</td>
                      <td className="px-4 py-3">
                        <Badge variant={statusBadgeVariant[p.status] || "secondary"} className="text-[10px]">
                          {p.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono">
                        <span className={cn(p.restart_count > 5 ? "text-rose-400 font-bold" : "text-muted-foreground")}>
                          {p.restart_count}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-sky-400">{p.cpu_usage_m}m</td>
                      <td className="px-4 py-3 text-xs font-mono text-purple-400">{p.memory_usage_mb}MB</td>
                      <td className="px-4 py-3">
                        <Button size="xs" variant="ghost" className="text-[10px] gap-1">
                          <Terminal className="h-3 w-3" /> Logs
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Container Details & Logs Drawer */}
      <ContainerDetailsDrawer pod={selectedPod} onClose={() => setSelectedPod(null)} />
    </div>
  );
}
