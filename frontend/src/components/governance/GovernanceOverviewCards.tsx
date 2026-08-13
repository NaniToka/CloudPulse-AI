import React from "react";
import { ShieldCheck, AlertTriangle, ShieldAlert, CheckCircle2, FileCheck } from "lucide-react";
import type { GovernanceOverviewResponse } from "@/types/governance";

interface GovernanceOverviewCardsProps {
  overview: GovernanceOverviewResponse | null;
}

export default function GovernanceOverviewCards({ overview }: GovernanceOverviewCardsProps) {
  if (!overview) return null;

  const getScoreBadgeColor = (score: number) => {
    if (score >= 90) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 75) return "text-blue-400 border-blue-500/30 bg-blue-500/10";
    if (score >= 60) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-rose-400 border-rose-500/30 bg-rose-500/10";
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 font-mono">
      {/* Overall Governance Score */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Governance Score</span>
          <ShieldCheck className="w-4 h-4 text-brand-blue" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-foreground">{overview.governance_score.toFixed(1)}</span>
          <span className="text-xs text-muted-foreground">/ 100</span>
        </div>
        <div className={`px-2 py-0.5 rounded text-[11px] font-semibold border inline-block ${getScoreBadgeColor(overview.governance_score)}`}>
          {overview.governance_rating}
        </div>
      </div>

      {/* Compliance Score */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Compliance Score</span>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <p className="text-2xl font-bold text-emerald-400">{overview.compliance_score.toFixed(1)}%</p>
        <p className="text-[11px] text-muted-foreground">{overview.passing_controls_count} / {overview.policies_evaluated_count} Policies Passed</p>
      </div>

      {/* Open Violations */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Open Violations</span>
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        </div>
        <p className="text-2xl font-bold text-amber-400">{overview.open_violations}</p>
        <p className="text-[11px] text-muted-foreground">Unresolved Non-Compliances</p>
      </div>

      {/* Critical Violations */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Critical Violations</span>
          <ShieldAlert className="w-4 h-4 text-rose-400" />
        </div>
        <p className="text-2xl font-bold text-rose-400">{overview.critical_violations}</p>
        <p className="text-[11px] text-muted-foreground">High Risk Exposure</p>
      </div>

      {/* Policies Evaluated */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Policies Evaluated</span>
          <FileCheck className="w-4 h-4 text-indigo-400" />
        </div>
        <p className="text-2xl font-bold text-indigo-300">{overview.policies_evaluated_count}</p>
        <p className="text-[11px] text-muted-foreground">Active Compliance Rules</p>
      </div>
    </div>
  );
}
