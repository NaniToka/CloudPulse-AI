/**
 * Statistical Anomaly Timeline Ledger Component
 */

import React from "react";
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Activity,
  CheckCircle2,
  Clock,
  Radio,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { AnomalyEvent } from "@/types/prediction";

interface AnomalyTimelineProps {
  anomalies: AnomalyEvent[];
  isLoading?: boolean;
}

export const AnomalyTimeline: React.FC<AnomalyTimelineProps> = ({
  anomalies,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 text-slate-400">
        <Activity className="mr-2 h-5 w-5 animate-spin text-indigo-400" />
        Scanning telemetry signals for anomalies...
      </div>
    );
  }

  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="flex h-48 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 text-center text-slate-400">
        <CheckCircle2 className="mb-2 h-8 w-8 text-emerald-400" />
        <div className="text-sm font-semibold text-slate-200">No Active Anomalies Detected</div>
        <div className="text-xs text-slate-500 mt-1">All telemetry channels are operating within statistical baselines.</div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Radio className="h-5 w-5 text-rose-400 animate-pulse" />
          <h3 className="text-base font-semibold text-white">Statistical Anomaly Ledger</h3>
          <Badge variant="outline" className="border-rose-500/30 bg-rose-500/10 text-rose-300">
            {anomalies.length} Signals
          </Badge>
        </div>
        <span className="text-xs text-slate-400">Z-Score & EWMA Multi-Method Detection</span>
      </div>

      <div className="mt-4 space-y-3 max-h-[380px] overflow-y-auto pr-1">
        {anomalies.map((anom) => {
          const isCritical = anom.severity === "CRITICAL";
          const isWarning = anom.severity === "WARNING";
          const isSpike = anom.direction === "SPIKE_HIGH";

          return (
            <div
              key={anom.id}
              className={`flex items-start justify-between rounded-lg border p-3.5 transition-all hover:bg-slate-800/40 ${
                isCritical
                  ? "border-rose-500/40 bg-rose-950/10"
                  : isWarning
                  ? "border-amber-500/30 bg-amber-950/10"
                  : "border-slate-800 bg-slate-950/40"
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`mt-0.5 rounded-md p-1.5 ${
                    isCritical
                      ? "bg-rose-500/20 text-rose-400"
                      : isWarning
                      ? "bg-amber-500/20 text-amber-400"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {isSpike ? (
                    <ArrowUpRight className="h-4 w-4" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4" />
                  )}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-200">
                      {anom.service}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      • {anom.metric_name.replace(/_/g, " ")}
                    </span>
                    <Badge
                      variant={isCritical ? "destructive" : isWarning ? "warning" : "secondary"}
                      className="text-[10px] py-0 px-1.5 uppercase font-mono"
                    >
                      {anom.severity}
                    </Badge>
                  </div>

                  <p className="mt-1 text-xs text-slate-300">
                    {anom.details?.explanation ||
                      `Anomaly detected: value ${anom.value.toFixed(1)} vs baseline ${anom.baseline_value.toFixed(1)} (Score: ${(anom.anomaly_score * 100).toFixed(0)}%)`}
                  </p>

                  <div className="mt-2 flex items-center gap-3 text-[11px] text-slate-500">
                    <span className="flex items-center gap-1 font-mono">
                      <Clock className="h-3 w-3" />
                      {new Date(anom.detected_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </span>
                    <span>Method: {anom.method || "z_score"}</span>
                    <span>Score: {anom.anomaly_score.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="text-sm font-bold text-slate-200 font-mono">
                  {anom.value.toFixed(1)}
                </div>
                <div className="text-[11px] text-slate-500 font-mono">
                  Base: {anom.baseline_value.toFixed(1)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
