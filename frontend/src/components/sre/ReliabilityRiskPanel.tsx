import React from "react";
import { AlertOctagon, ShieldAlert, ArrowRight } from "lucide-react";
import type { ReliabilityRiskItem } from "@/types/sre";

interface ReliabilityRiskPanelProps {
  risks: ReliabilityRiskItem[];
}

export default function ReliabilityRiskPanel({ risks }: ReliabilityRiskPanelProps) {
  if (!risks || risks.length === 0) {
    return (
      <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 text-center space-y-1">
        <p className="text-xs text-muted-foreground">No reliability risks or SLO breaches currently detected.</p>
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
          <h3 className="text-sm font-semibold text-foreground">Reliability Risks & Breach Warnings</h3>
        </div>
        <span className="text-xs font-mono text-rose-300 font-semibold">{risks.length} Risks Identified</span>
      </div>

      <div className="space-y-3">
        {risks.map((item) => (
          <div key={item.id} className="p-4 rounded-lg border border-white/5 bg-black/40 space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                {getSeverityBadge(item.severity)}
                <h4 className="text-xs font-semibold text-foreground">{item.risk}</h4>
                <span className="text-[11px] font-mono text-muted-foreground">({item.service})</span>
              </div>
              <span className="text-[11px] font-mono text-muted-foreground">Metric: {item.metric} ({item.current_value} vs {item.threshold})</span>
            </div>

            <p className="text-xs text-muted-foreground">{item.explanation}</p>

            <div className="pt-1 flex items-center gap-1.5 text-xs font-mono text-brand-blue">
              <ArrowRight className="w-3.5 h-3.5" />
              <span>Action: {item.recommended_action}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
