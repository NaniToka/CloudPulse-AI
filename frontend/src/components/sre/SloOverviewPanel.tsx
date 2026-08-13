import React from "react";
import { Target, CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react";
import type { SloItem } from "@/types/sre";

interface SloOverviewPanelProps {
  slos: SloItem[];
}

export default function SloOverviewPanel({ slos }: SloOverviewPanelProps) {
  const getStatusBadge = (status: string) => {
    if (status === "BREACHED") {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">BREACHED</span>;
    }
    if (status === "AT_RISK") {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">AT RISK</span>;
    }
    return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">HEALTHY</span>;
  };

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-semibold text-foreground">Service Level Objectives (SLOs)</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">{slos.length} Active Targets</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {slos.map((slo) => (
          <div key={slo.id} className="p-4 rounded-lg border border-white/5 bg-black/20 space-y-2.5">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-xs font-semibold text-foreground">{slo.name}</h4>
                <p className="text-[11px] text-muted-foreground font-mono">
                  Svc: {slo.service} | Window: {slo.window}
                </p>
              </div>
              {getStatusBadge(slo.status)}
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-muted-foreground">
                  Target: <strong className="text-foreground">{slo.target}%</strong> {slo.target_threshold_ms ? `(< ${slo.target_threshold_ms}ms)` : ""}
                </span>
                <span className="text-foreground font-semibold">Actual: {slo.current_sli}{slo.indicator_type === "latency" ? "ms" : "%"}</span>
              </div>

              <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    slo.status === "BREACHED" ? "bg-rose-500" : slo.status === "AT_RISK" ? "bg-amber-500" : "bg-emerald-400"
                  }`}
                  style={{ width: `${Math.min(100, slo.compliance_percentage)}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
