import React from "react";
import { AlertCircle, Clock, ShieldAlert } from "lucide-react";
import type { IncidentImpactItem } from "@/types/sre";

interface IncidentImpactPanelProps {
  incidents: IncidentImpactItem[];
}

export default function IncidentImpactPanel({ incidents }: IncidentImpactPanelProps) {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 text-center text-xs text-muted-foreground">
        No open incidents currently impacting SLO targets or error budgets.
      </div>
    );
  }

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-semibold text-foreground">Incident Command Center Correlation</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">{incidents.length} Active Incidents</span>
      </div>

      <div className="space-y-3">
        {incidents.map((inc) => (
          <div key={inc.id} className="p-3.5 rounded-lg border border-white/5 bg-black/30 flex flex-col md:flex-row md:items-center justify-between gap-3 font-mono text-xs">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {inc.severity}
                </span>
                <span className="font-semibold text-foreground">{inc.title}</span>
              </div>
              <p className="text-[11px] text-muted-foreground">
                Affected Svc: <strong className="text-foreground">{inc.service}</strong> | Status: {inc.status}
              </p>
            </div>

            <div className="flex items-center gap-4 text-right shrink-0">
              <div>
                <span className="block text-[10px] text-muted-foreground">Duration</span>
                <span className="text-foreground font-semibold">{inc.duration_minutes.toFixed(0)} mins</span>
              </div>
              <div>
                <span className="block text-[10px] text-muted-foreground">Budget Impact</span>
                <span className="text-rose-400 font-bold">-{inc.budget_impact_pct}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
