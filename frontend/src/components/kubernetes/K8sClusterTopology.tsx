import React from "react";
import { Server, Box, Cpu, Network, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export default function K8sClusterTopology() {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/80 p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Network className="h-4 w-4 text-sky-400" />
            Interactive Kubernetes Cluster Topology
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Node-to-Pod container hierarchy & networking layout
          </p>
        </div>
        <Badge variant="outline" className="border-sky-500/40 text-sky-400 font-mono text-[10px]">
          gke-us-central1-prod
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        {/* Node 1 */}
        <div className="rounded-lg border border-sky-500/30 bg-sky-500/[0.03] p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-sky-400 font-mono flex items-center gap-1.5">
              <Server className="h-3.5 w-3.5" /> gke-node-pool-1-a8b2
            </span>
            <Badge variant="success" className="text-[9px]">
              Ready (45% CPU)
            </Badge>
          </div>
          <div className="space-y-2">
            <div className="rounded border border-white/10 bg-background/80 p-2.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-foreground">api-gateway-7b9f88c</span>
                <span className="text-[10px] text-emerald-400 font-mono">Running</span>
              </div>
              <p className="text-[10px] text-muted-foreground">gcr.io/cloudpulse/api-gateway:v2.14.1 · 140m CPU</p>
            </div>
            <div className="rounded border border-white/10 bg-background/80 p-2.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-foreground">auth-service-589d7b</span>
                <span className="text-[10px] text-emerald-400 font-mono">Running</span>
              </div>
              <p className="text-[10px] text-muted-foreground">gcr.io/cloudpulse/auth-service:v1.8.3 · 85m CPU</p>
            </div>
          </div>
        </div>

        {/* Node 2 */}
        <div className="rounded-lg border border-rose-500/30 bg-rose-500/[0.03] p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-400 font-mono flex items-center gap-1.5">
              <Server className="h-3.5 w-3.5" /> gke-node-pool-1-c9d4
            </span>
            <Badge variant="warning" className="text-[9px]">
              Ready (81% CPU)
            </Badge>
          </div>
          <div className="space-y-2">
            <div className="rounded border border-rose-500/40 bg-rose-500/10 p-2.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-foreground">payment-svc-67d4fc</span>
                <span className="text-[10px] text-rose-400 font-mono font-bold animate-pulse">CrashLoopBackOff</span>
              </div>
              <p className="text-[10px] text-muted-foreground">gcr.io/cloudpulse/payment-svc:v3.2.0 · 14 Restarts</p>
            </div>
            <div className="rounded border border-rose-500/40 bg-rose-500/10 p-2.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-foreground">payment-svc-67d4fc-p4q7</span>
                <span className="text-[10px] text-rose-400 font-mono font-bold">OOMKilled</span>
              </div>
              <p className="text-[10px] text-muted-foreground">Limit 1024Mi Exceeded · Exit 137</p>
            </div>
          </div>
        </div>

        {/* Node 3 */}
        <div className="rounded-lg border border-purple-500/30 bg-purple-500/[0.03] p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-purple-400 font-mono flex items-center gap-1.5">
              <Server className="h-3.5 w-3.5" /> gke-node-pool-2-g3h5
            </span>
            <Badge variant="success" className="text-[9px]">
              Ready (58% Memory)
            </Badge>
          </div>
          <div className="space-y-2">
            <div className="rounded border border-white/10 bg-background/80 p-2.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-foreground">data-pipeline-worker</span>
                <span className="text-[10px] text-amber-400 font-mono">Pending</span>
              </div>
              <p className="text-[10px] text-muted-foreground">Insufficient Memory on node pool</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
