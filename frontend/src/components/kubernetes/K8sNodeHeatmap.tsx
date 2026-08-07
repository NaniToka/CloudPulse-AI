import React from "react";
import { Server, Cpu, HardDrive, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { K8sNodeItem } from "@/services/kubernetesService";
import { cn } from "@/lib/utils";

interface K8sNodeHeatmapProps {
  nodes: K8sNodeItem[];
}

export default function K8sNodeHeatmap({ nodes }: K8sNodeHeatmapProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Cpu className="h-4 w-4 text-sky-400" />
            Cluster Node Utilization Heatmap
          </CardTitle>
          <span className="text-xs text-muted-foreground">{nodes.length} Nodes Active</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {nodes.map((node) => {
            const cpuVal = node.cpu_percent ?? 0;
            const memVal = node.memory_percent ?? 0;
            const diskVal = node.disk_percent ?? 0;

            const isHigh = cpuVal > 80 || memVal > 80;

            return (
              <div
                key={node.id}
                className={cn(
                  "rounded-lg border p-4 space-y-3 transition-all",
                  isHigh ? "border-rose-500/40 bg-rose-500/[0.03]" : "border-white/10 bg-white/[0.02]"
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-foreground">{node.name}</span>
                  <span
                    className={cn(
                      "text-[10px] font-mono font-semibold px-2 py-0.5 rounded",
                      node.status === "Ready" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                    )}
                  >
                    {node.status}
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div>
                    <div className="flex justify-between text-[10px] text-muted-foreground mb-1">
                      <span>CPU Utilization</span>
                      <span className="font-mono">{cpuVal.toFixed(0)}%</span>
                    </div>
                    <Progress value={cpuVal} className="h-1.5" indicatorClassName={cpuVal > 80 ? "bg-rose-500" : "bg-sky-500"} />
                  </div>

                  <div>
                    <div className="flex justify-between text-[10px] text-muted-foreground mb-1">
                      <span>Memory Utilization</span>
                      <span className="font-mono">{memVal.toFixed(0)}%</span>
                    </div>
                    <Progress value={memVal} className="h-1.5" indicatorClassName={memVal > 80 ? "bg-amber-500" : "bg-purple-500"} />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1 text-[10px] text-muted-foreground font-mono">
                  <span>{node.instance_type}</span>
                  <span>{node.pods_running}/{node.pod_capacity} Pods</span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
