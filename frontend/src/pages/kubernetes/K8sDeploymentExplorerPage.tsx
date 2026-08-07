import { useState } from "react";
import { Box, Search, RefreshCw, Loader2, GitCommit } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useK8sDeployments } from "@/hooks/useKubernetes";

export default function K8sDeploymentExplorerPage() {
  const { data: deployments = [], isLoading, refetch } = useK8sDeployments();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Deployment & Workload Explorer"
        subtitle="Kubernetes deployments, replica sets, rollout strategies, and container image versions"
        actions={
          <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-2 text-xs">
            <RefreshCw className="h-3.5 w-3.5" /> Refresh Workloads
          </Button>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-semibold text-foreground">Deployments Registry ({deployments.length})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" /> Querying Kubernetes Deployments...
            </div>
          ) : deployments.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground">No active deployments found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                    {["Deployment Name", "Namespace", "Replicas (Ready/Desired)", "Rollout Strategy", "Container Image"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {deployments.map((d) => {
                    const ratio = (d.ready_replicas / (d.desired_replicas || 1)) * 100;
                    return (
                      <tr key={d.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3 font-mono text-xs font-semibold text-foreground">{d.name}</td>
                        <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{d.namespace}</td>
                        <td className="px-4 py-3 min-w-[140px]">
                          <div className="flex items-center gap-2">
                            <Progress value={ratio} className="h-1.5 w-16" indicatorClassName={ratio === 100 ? "bg-emerald-400" : "bg-amber-400"} />
                            <span className="text-xs font-mono text-muted-foreground">
                              {d.ready_replicas}/{d.desired_replicas}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant="outline" className="text-[10px] font-mono">
                            {d.strategy}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-xs font-mono text-muted-foreground truncate max-w-xs">{d.image}</td>
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
