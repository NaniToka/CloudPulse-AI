import React from "react";
import { AlertOctagon, TrendingUp, AlertTriangle } from "lucide-react";
import type { CostAnomalyItem } from "@/types/cost";

interface CostAnomalyPanelProps {
  anomalies: CostAnomalyItem[];
}

export default function CostAnomalyPanel({ anomalies }: CostAnomalyPanelProps) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 text-center space-y-1">
        <p className="text-xs text-muted-foreground">No cost anomalies or spending spikes detected across resources.</p>
      </div>
    );
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">HIGH</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">MEDIUM</span>;
    }
  };

  return (
    <div className="p-5 rounded-xl border border-rose-500/20 bg-rose-500/5 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-rose-400" />
          <h3 className="text-sm font-semibold text-foreground">Detected Cost Anomalies & Spikes</h3>
        </div>
        <span className="text-xs font-mono text-rose-300 font-semibold">
          {anomalies.length} Anomalies Flagged
        </span>
      </div>

      <div className="space-y-3">
        {anomalies.map((item) => (
          <div
            key={item.id}
            className="p-3.5 rounded-lg border border-white/5 bg-black/40 flex flex-col md:flex-row md:items-center justify-between gap-3"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                {getSeverityBadge(item.severity)}
                <span className="text-xs font-mono font-bold text-foreground">{item.resource}</span>
                <span className="text-[11px] font-mono text-muted-foreground">({item.provider} / {item.service})</span>
              </div>
              <p className="text-xs text-muted-foreground">{item.explanation}</p>
            </div>

            <div className="flex items-center gap-4 text-right font-mono shrink-0">
              <div>
                <span className="block text-[10px] text-muted-foreground">Expected vs Actual</span>
                <span className="text-xs text-foreground font-semibold">
                  ${item.expected_cost.toLocaleString()} &rarr; <strong className="text-rose-400">${item.actual_cost.toLocaleString()}</strong>
                </span>
              </div>
              <div>
                <span className="block text-[10px] text-muted-foreground">Difference</span>
                <span className="text-xs text-rose-400 font-bold">+${item.difference.toLocaleString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
