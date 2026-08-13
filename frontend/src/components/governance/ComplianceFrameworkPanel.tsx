import React from "react";
import { Shield, Info } from "lucide-react";
import type { ComplianceFrameworkItem } from "@/types/governance";

interface ComplianceFrameworkPanelProps {
  frameworks: ComplianceFrameworkItem[];
}

export default function ComplianceFrameworkPanel({ frameworks }: ComplianceFrameworkPanelProps) {
  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-brand-blue" />
          <h3 className="text-sm font-semibold text-foreground">Compliance Framework Control Mappings</h3>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-[11px] text-amber-300 font-bold">
          <Info className="w-3.5 h-3.5" />
          <span>Internal Control Mapping — Not a Certification</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        {frameworks.map((fw) => (
          <div key={fw.framework} className="p-3.5 rounded-lg border border-white/5 bg-black/30 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-foreground">{fw.framework}</span>
              <span className="text-[10px] text-muted-foreground">{fw.version}</span>
            </div>

            <div className="flex items-baseline justify-between">
              <span className="text-xl font-bold text-foreground">{fw.compliance_score.toFixed(1)}%</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${fw.status === "PASS" ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}>
                {fw.status}
              </span>
            </div>

            <div className="space-y-1">
              <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${fw.compliance_score >= 85 ? "bg-emerald-400" : "bg-amber-500"}`}
                  style={{ width: `${fw.compliance_score}%` }}
                />
              </div>
              <p className="text-[10px] text-muted-foreground">
                Passing: {fw.passing_controls} / {fw.total_controls} controls
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
