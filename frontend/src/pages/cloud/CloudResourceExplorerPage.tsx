import { useState } from "react";
import { Server, Search, Filter, Cpu, HardDrive, DollarSign, ShieldAlert, X, Activity, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useCloudResources } from "@/hooks/useCloudObservability";
import type { CloudResourceItem } from "@/services/cloudService";
import { cn } from "@/lib/utils";

const providerBadge: Record<string, string> = {
  AWS: "text-amber-400 border-amber-500/30 bg-amber-500/10",
  GCP: "text-sky-400 border-sky-500/30 bg-sky-500/10",
  Azure: "text-purple-400 border-purple-500/30 bg-purple-500/10",
};

export default function CloudResourceExplorerPage() {
  const [search, setSearch] = useState("");
  const [provider, setProvider] = useState("all");
  const [resourceType, setResourceType] = useState("all");
  const [selectedResource, setSelectedResource] = useState<CloudResourceItem | null>(null);

  const { data: resources = [], isLoading } = useCloudResources({
    search: search || undefined,
    provider: provider === "all" ? undefined : provider,
    resource_type: resourceType === "all" ? undefined : resourceType,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multi-Cloud Resource Explorer"
        subtitle="Auto-discovered infrastructure inventory across AWS, GCP & Azure"
      />

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
          <CardTitle className="text-sm font-semibold text-foreground">Discovered Resources ({resources.length})</CardTitle>
          <div className="flex items-center gap-3">
            <Input
              placeholder="Search resource name or service..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-56 text-xs"
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
            <select
              value={resourceType}
              onChange={(e) => setResourceType(e.target.value)}
              className="h-8 rounded-md border border-white/10 bg-background px-2 text-xs text-foreground"
            >
              <option value="all">All Types</option>
              <option value="kubernetes_cluster">Kubernetes</option>
              <option value="virtual_machine">Virtual Machines</option>
              <option value="database">Databases</option>
              <option value="storage">Storage</option>
              <option value="function">Serverless Functions</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" /> Querying multi-cloud inventory...
            </div>
          ) : resources.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground">No resources match the selected filters.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                    {["Resource Name", "Service", "Provider", "Region", "Status", "Monthly Cost", "Risk Score", "Actions"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {resources.map((r) => (
                    <tr
                      key={r.id}
                      onClick={() => setSelectedResource(r)}
                      className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3 font-mono text-xs font-semibold text-foreground">{r.name}</td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">{r.service}</td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className={cn("text-[10px]", providerBadge[r.provider] || "text-foreground")}>
                          {r.provider}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{r.region}</td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={r.status === "healthy" ? "success" : r.status === "warning" ? "warning" : "danger"}
                          className="text-[10px]"
                        >
                          {r.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-foreground font-semibold">${r.monthly_cost.toFixed(2)}</td>
                      <td className="px-4 py-3 text-xs font-mono">
                        <span className={cn(r.risk_score > 30 ? "text-rose-400 font-bold" : "text-emerald-400")}>
                          {r.risk_score}/100
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Button size="xs" variant="ghost" className="text-[10px]">
                          Inspect
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

      {/* Resource Details Drawer */}
      {selectedResource && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md border-l border-white/10 bg-slate-950 p-6 shadow-2xl space-y-6 overflow-y-auto">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <h3 className="text-sm font-bold text-foreground font-mono">{selectedResource.name}</h3>
              <p className="text-xs text-muted-foreground">
                {selectedResource.service} · {selectedResource.provider} {selectedResource.region}
              </p>
            </div>
            <button onClick={() => setSelectedResource(null)} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
                <span className="text-[10px] text-muted-foreground">Monthly Cost</span>
                <p className="text-lg font-bold text-amber-400">${selectedResource.monthly_cost.toFixed(2)}</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
                <span className="text-[10px] text-muted-foreground">Risk Score</span>
                <p className={cn("text-lg font-bold", selectedResource.risk_score > 30 ? "text-rose-400" : "text-emerald-400")}>
                  {selectedResource.risk_score}/100
                </p>
              </div>
            </div>

            <div className="space-y-3 rounded-lg border border-white/10 bg-white/[0.02] p-4">
              <h4 className="font-semibold text-foreground text-xs">Resource Telemetry</h4>
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-[11px] text-muted-foreground mb-1">
                    <span>CPU Utilization</span>
                    <span>{(selectedResource.cpu_percent ?? 0).toFixed(1)}%</span>
                  </div>
                  <Progress value={selectedResource.cpu_percent ?? 0} className="h-1.5" />
                </div>
                <div>
                  <div className="flex justify-between text-[11px] text-muted-foreground mb-1">
                    <span>Memory Utilization</span>
                    <span>{(selectedResource.memory_percent ?? 0).toFixed(1)}%</span>
                  </div>
                  <Progress value={selectedResource.memory_percent ?? 0} className="h-1.5" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
