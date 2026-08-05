/**
 * Kubernetes Pods Table Component — Displays live streaming K8s Pod Telemetry.
 */

import React, { memo } from "react";
import { Server, RefreshCw, Cpu, HardDrive } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { K8sPodStatus } from "@/types/metric";

interface K8sPodsTableProps {
  pods: K8sPodStatus[];
}

export const K8sPodsTable: React.FC<K8sPodsTableProps> = memo(({ pods }) => {
  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-xl">
      <CardHeader className="p-4 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Server className="h-4 w-4 text-brand-purple" />
          <CardTitle className="text-xs font-semibold text-foreground">
            Kubernetes Pod Status Telemetry
          </CardTitle>
        </div>
        <span className="text-[10px] text-muted-foreground font-mono">
          Namespace: prod / data
        </span>
      </CardHeader>

      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/10 text-muted-foreground bg-bg-elevated/40">
                <th className="px-4 py-2.5 text-left font-medium">Pod Name</th>
                <th className="px-4 py-2.5 text-left font-medium">Service</th>
                <th className="px-4 py-2.5 text-left font-medium">Node</th>
                <th className="px-4 py-2.5 text-left font-medium">Status</th>
                <th className="px-4 py-2.5 text-left font-medium">CPU %</th>
                <th className="px-4 py-2.5 text-left font-medium">Memory</th>
                <th className="px-4 py-2.5 text-right font-medium">Restarts</th>
              </tr>
            </thead>
            <tbody>
              {pods.map((pod, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.03] transition-colors">
                  <td className="px-4 py-2.5 font-mono text-foreground font-medium truncate max-w-[200px]">
                    {pod.name}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-muted-foreground">{pod.service}</td>
                  <td className="px-4 py-2.5 font-mono text-muted-foreground">{pod.node}</td>
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-950/40 text-emerald-400 border border-emerald-500/30">
                      <span className={`h-1.5 w-1.5 rounded-full ${pod.status === 'Running' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
                      {pod.status}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-foreground">{pod.cpu_percent.toFixed(1)}%</td>
                  <td className="px-4 py-2.5 font-mono text-foreground">{pod.memory_mb.toFixed(0)} MB</td>
                  <td className="px-4 py-2.5 font-mono text-right text-muted-foreground">{pod.restarts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
});

K8sPodsTable.displayName = "K8sPodsTable";
