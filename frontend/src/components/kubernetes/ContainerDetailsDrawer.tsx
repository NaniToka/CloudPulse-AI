import React from "react";
import { Terminal, X, RefreshCw, Cpu, HardDrive, AlertTriangle, ShieldCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useK8sPodLogs } from "@/hooks/useKubernetes";
import type { K8sPodItem } from "@/services/kubernetesService";
import { cn } from "@/lib/utils";

interface ContainerDetailsDrawerProps {
  pod: K8sPodItem | null;
  onClose: () => void;
}

export default function ContainerDetailsDrawer({ pod, onClose }: ContainerDetailsDrawerProps) {
  const { data: logData, isLoading: logsLoading, refetch } = useK8sPodLogs(pod?.name ?? null);

  if (!pod) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl border-l border-white/10 bg-slate-950 p-6 shadow-2xl space-y-6 overflow-y-auto backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h3 className="text-sm font-bold text-foreground font-mono flex items-center gap-2">
            <Terminal className="h-4 w-4 text-sky-400" />
            {pod.name}
          </h3>
          <p className="text-xs text-muted-foreground">
            Namespace: <span className="font-mono text-foreground">{pod.namespace}</span> · Deployment: <span className="font-mono text-foreground">{pod.deployment_name || "standalone"}</span>
          </p>
        </div>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Health & Status Cards */}
      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
          <span className="text-[10px] text-muted-foreground">Pod Status</span>
          <p className="font-bold text-foreground flex items-center gap-1.5">
            <Badge variant={pod.status === "Running" ? "success" : "danger"} className="text-[10px]">
              {pod.status}
            </Badge>
          </p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
          <span className="text-[10px] text-muted-foreground">Restart Count</span>
          <p className={cn("text-base font-bold font-mono", pod.restart_count > 5 ? "text-rose-400" : "text-foreground")}>
            {pod.restart_count}
          </p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
          <span className="text-[10px] text-muted-foreground">CPU Usage</span>
          <p className="text-base font-bold font-mono text-sky-400">{pod.cpu_usage_m}m</p>
        </div>
      </div>

      {/* Live Container Logs */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold text-foreground flex items-center gap-2">
            <Terminal className="h-3.5 w-3.5 text-sky-400" />
            Live Container Logs (stdout/stderr)
          </h4>
          <Button size="xs" variant="ghost" onClick={() => refetch()} className="h-6 text-[10px] gap-1 text-muted-foreground">
            <RefreshCw className="h-3 w-3" /> Refetch
          </Button>
        </div>

        <div className="rounded-lg border border-white/10 bg-black/90 p-4 font-mono text-[11px] leading-relaxed text-slate-300 space-y-1 max-h-60 overflow-y-auto">
          {logsLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Tailing pod logs...
            </div>
          ) : (
            logData?.logs?.map((line, idx) => (
              <div key={idx} className={cn(line.includes("ERROR") || line.includes("FATAL") ? "text-rose-400" : line.includes("WARN") ? "text-amber-400" : "text-slate-300")}>
                {line}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Container Image details */}
      <div className="rounded-lg border border-white/10 bg-white/[0.02] p-4 space-y-2 text-xs">
        <h4 className="font-semibold text-foreground text-xs">Container Specs</h4>
        <div className="space-y-1 font-mono text-[11px] text-muted-foreground">
          <p><span className="text-foreground">Image:</span> gcr.io/cloudpulse/app:v2.14.1</p>
          <p><span className="text-foreground">Requests:</span> 100m CPU, 256Mi Memory</p>
          <p><span className="text-foreground">Limits:</span> 500m CPU, 1024Mi Memory</p>
        </div>
      </div>
    </div>
  );
}
