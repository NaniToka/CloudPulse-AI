import React, { useEffect, useRef } from "react";
import { Terminal, X, RefreshCw, Cpu, HardDrive, AlertTriangle, ShieldCheck, Loader2, Circle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useK8sPodLogs } from "@/hooks/useKubernetes";
import type { K8sPodItem } from "@/services/kubernetesService";
import { cn } from "@/lib/utils";

interface ContainerDetailsDrawerProps {
  pod: K8sPodItem | null;
  onClose: () => void;
}

export default function ContainerDetailsDrawer({ pod, onClose }: ContainerDetailsDrawerProps) {
  const { data: logData, isLoading: logsLoading, isFetching, refetch } = useK8sPodLogs(pod?.name ?? null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logData]);

  if (!pod) return null;

  const logsList = logData?.logs || [];

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/60 backdrop-blur-sm transition-all duration-300">
      {/* Click outside backdrop */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Drawer Container */}
      <div className="relative z-10 w-full max-w-xl border-l border-slate-800/80 bg-slate-950/95 p-6 shadow-2xl space-y-6 overflow-y-auto backdrop-blur-2xl flex flex-col justify-between h-full">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="min-w-0 flex-1 pr-4">
              <h3 className="text-base font-bold text-white font-mono flex items-center gap-2 truncate">
                <div className="p-1.5 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-400 shrink-0">
                  <Terminal className="h-4 w-4" />
                </div>
                <span className="truncate" title={pod.name}>{pod.name}</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1 truncate">
                Namespace: <span className="font-mono font-bold text-slate-200">{pod.namespace}</span> · Deployment:{" "}
                <span className="font-mono font-bold text-slate-200">{pod.deployment_name || "standalone"}</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors shrink-0"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Health & Status Cards */}
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3 space-y-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Pod Status</span>
              <div className="pt-0.5">
                <span
                  className={cn(
                    "px-2.5 py-0.5 text-[10px] font-extrabold uppercase rounded-full border inline-block",
                    pod.status === "Running"
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                      : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                  )}
                >
                  {pod.status}
                </span>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3 space-y-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Restart Count</span>
              <p
                className={cn(
                  "text-sm font-bold font-mono",
                  pod.restart_count > 5 ? "text-rose-400" : "text-slate-200"
                )}
              >
                {pod.restart_count}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3 space-y-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">CPU Usage</span>
              <p className="text-sm font-bold font-mono text-sky-400">{pod.cpu_usage_m}m</p>
            </div>
          </div>

          {/* Live Container Logs */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-white flex items-center gap-2">
                <Terminal className="h-3.5 w-3.5 text-sky-400" />
                Live Container Logs (stdout/stderr)
              </h4>
              <Button
                size="xs"
                variant="ghost"
                onClick={() => refetch()}
                disabled={isFetching}
                className="h-7 text-[11px] gap-1.5 text-slate-300 hover:text-white bg-slate-900 border border-slate-800 hover:bg-slate-800 px-2.5 rounded-lg"
              >
                <RefreshCw className={cn("h-3 w-3", isFetching && "animate-spin text-sky-400")} />
                Refetch
              </Button>
            </div>

            {/* Terminal Window Box */}
            <div className="rounded-xl border border-slate-800/90 bg-slate-950 overflow-hidden shadow-inner">
              {/* Terminal Window Header Bar */}
              <div className="bg-slate-900/90 px-3 py-2 border-b border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <div className="flex items-center gap-1.5">
                  <Circle className="w-2.5 h-2.5 fill-rose-500 text-rose-500" />
                  <Circle className="w-2.5 h-2.5 fill-amber-500 text-amber-500" />
                  <Circle className="w-2.5 h-2.5 fill-emerald-500 text-emerald-500" />
                  <span className="ml-2 text-[10px] text-slate-400 font-bold">stdout/stderr stream</span>
                </div>
                <span className="text-[10px] text-slate-400">{logsList.length} lines</span>
              </div>

              {/* Log Stream Content Area */}
              <div
                ref={logContainerRef}
                className="p-4 font-mono text-[11px] leading-relaxed text-slate-300 space-y-1.5 min-h-[180px] max-h-72 overflow-y-auto bg-black/95 select-text"
              >
                {logsLoading ? (
                  <div className="flex items-center justify-center py-12 gap-2 text-slate-400 text-xs">
                    <Loader2 className="h-4 w-4 animate-spin text-sky-400" /> Tailing pod container logs...
                  </div>
                ) : logsList.length === 0 ? (
                  <div className="text-center py-12 text-slate-500 text-xs font-sans">
                    No log output emitted for container process.
                  </div>
                ) : (
                  logsList.map((line, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        "flex items-start gap-2 py-0.5",
                        line.includes("ERROR") || line.includes("FATAL")
                          ? "text-rose-400 bg-rose-950/20 px-1 rounded"
                          : line.includes("WARN")
                          ? "text-amber-400 bg-amber-950/20 px-1 rounded"
                          : line.includes("200 OK") || line.includes("201 Created")
                          ? "text-emerald-400"
                          : "text-slate-300"
                      )}
                    >
                      <span className="text-slate-600 text-[10px] select-none w-6 shrink-0 text-right font-mono">
                        {idx + 1}
                      </span>
                      <span className="break-all">{line}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Container Specs */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-2 text-xs">
            <h4 className="font-bold text-white text-xs">Container Specs & Quotas</h4>
            <div className="space-y-1.5 font-mono text-[11px] text-slate-300">
              <p>
                <span className="text-slate-400 font-bold">Image:</span> gcr.io/cloudpulse/app:v2.14.1
              </p>
              <p>
                <span className="text-slate-400 font-bold">Requests:</span> 100m CPU, 256Mi Memory
              </p>
              <p>
                <span className="text-slate-400 font-bold">Limits:</span> 500m CPU, 1024Mi Memory
              </p>
            </div>
          </div>
        </div>

        {/* Footer actions */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
          <span className="text-slate-400 font-mono text-[11px]">Cluster ID: gke-prod-us-central1</span>
          <Button size="sm" variant="outline" onClick={onClose} className="border-slate-800 hover:bg-slate-900 text-slate-200">
            Close Drawer
          </Button>
        </div>
      </div>
    </div>
  );
}
