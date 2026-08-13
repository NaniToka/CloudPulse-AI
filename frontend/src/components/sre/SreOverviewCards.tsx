import React from "react";
import { ShieldCheck, AlertTriangle, ShieldAlert, Activity, PieChart } from "lucide-react";
import type { SreOverviewResponse } from "@/types/sre";

interface SreOverviewCardsProps {
  overview: SreOverviewResponse | null;
}

export default function SreOverviewCards({ overview }: SreOverviewCardsProps) {
  if (!overview) return null;

  const getScoreBadgeColor = (score: number) => {
    if (score >= 95) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 85) return "text-blue-400 border-blue-500/30 bg-blue-500/10";
    if (score >= 70) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-rose-400 border-rose-500/30 bg-rose-500/10";
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Overall Reliability Score */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-muted-foreground">Overall Reliability</span>
          <Activity className="w-4 h-4 text-brand-blue" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-foreground">{overview.overall_score.toFixed(1)}</span>
          <span className="text-xs text-muted-foreground">/ 100</span>
        </div>
        <div className={`px-2 py-0.5 rounded text-[11px] font-semibold border inline-block ${getScoreBadgeColor(overview.overall_score)}`}>
          {overview.overall_rating}
        </div>
      </div>

      {/* Healthy Services */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-muted-foreground">Healthy Services</span>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>
        <p className="text-2xl font-bold font-mono text-emerald-400">{overview.services_healthy}</p>
        <p className="text-[11px] text-muted-foreground">Meeting target SLO limits</p>
      </div>

      {/* Services At Risk */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-muted-foreground">Services At Risk</span>
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        </div>
        <p className="text-2xl font-bold font-mono text-amber-400">{overview.services_at_risk}</p>
        <p className="text-[11px] text-muted-foreground">Elevated burn rate / latency</p>
      </div>

      {/* SLO Breaches */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-muted-foreground">SLO Breaches</span>
          <ShieldAlert className="w-4 h-4 text-rose-400" />
        </div>
        <p className="text-2xl font-bold font-mono text-rose-400">{overview.slo_breaches}</p>
        <p className="text-[11px] text-muted-foreground">Active target violations</p>
      </div>

      {/* Error Budget Avg */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-muted-foreground">Error Budget Avg</span>
          <PieChart className="w-4 h-4 text-indigo-400" />
        </div>
        <p className="text-2xl font-bold font-mono text-indigo-300">{overview.error_budget_remaining_avg.toFixed(1)}%</p>
        <p className="text-[11px] text-muted-foreground">Remaining 30-day budget</p>
      </div>
    </div>
  );
}
