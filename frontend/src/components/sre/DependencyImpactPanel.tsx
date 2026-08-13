import React from "react";
import { GitFork, AlertTriangle } from "lucide-react";
import type { DependencyImpactItem } from "@/types/sre";

interface DependencyImpactPanelProps {
  dependencies: DependencyImpactItem[];
}

export default function DependencyImpactPanel({ dependencies }: DependencyImpactPanelProps) {
  if (!dependencies || dependencies.length === 0) return null;

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitFork className="w-5 h-5 text-brand-blue" />
          <h3 className="text-sm font-semibold text-foreground">Dependency DAG Reliability & Blast Radius</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">{dependencies.length} Tracked Links</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
        {dependencies.map((dep, idx) => (
          <div key={idx} className="p-3.5 rounded-lg border border-white/5 bg-black/20 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-foreground">{dep.dependency} → {dep.target_service}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${dep.health === "DEGRADED" ? "bg-amber-500/20 text-amber-300" : "bg-emerald-500/20 text-emerald-300"}`}>
                {dep.health}
              </span>
            </div>

            <div className="text-[11px] text-muted-foreground space-y-0.5">
              <p>P99 Latency: <strong className="text-foreground">{dep.latency_ms}ms</strong></p>
              <p>Error Rate: <strong className="text-foreground">{dep.error_rate}%</strong></p>
              <p>Risk: <span className="text-amber-300">{dep.reliability_risk}</span></p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
