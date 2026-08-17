import React from "react";
import { ShieldCheck, AlertTriangle, Info, TrendingUp, DollarSign } from "lucide-react";
import type { CostHealthScoreResponse, ExecutiveCostSummaryResponse } from "@/types/cost";

interface ExecutiveHealthCardProps {
  healthScore: CostHealthScoreResponse | null;
  executiveSummary: ExecutiveCostSummaryResponse | null;
}

export default function ExecutiveHealthCard({ healthScore, executiveSummary }: ExecutiveHealthCardProps) {
  if (!healthScore) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Healthy":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
      case "Watch":
        return "text-amber-400 bg-amber-500/10 border-amber-500/30";
      case "At Risk":
        return "text-orange-400 bg-orange-500/10 border-orange-500/30";
      default:
        return "text-rose-400 bg-rose-500/10 border-rose-500/30";
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
      {/* FinOps Health Score Card */}
      <div className="lg:col-span-5 p-5 rounded-xl border border-white/[0.08] bg-bg-surface space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-brand-blue" />
            <h3 className="text-sm font-semibold text-foreground">FinOps Health Score</h3>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusColor(healthScore.status)}`}>
            {healthScore.status} Posture
          </span>
        </div>

        <div className="flex items-center gap-6 py-2">
          <div className="relative w-24 h-24 flex items-center justify-center rounded-full bg-slate-900 border-4 border-brand-blue/30 shadow-inner">
            <div className="text-center">
              <span className="text-2xl font-bold font-mono text-foreground">{healthScore.score}</span>
              <span className="text-[10px] block text-muted-foreground font-mono">/ 100</span>
            </div>
          </div>
          <div className="space-y-1.5 flex-1">
            <p className="text-xs text-muted-foreground leading-relaxed">{healthScore.explanation}</p>
          </div>
        </div>

        {/* Health Factors */}
        <div className="space-y-1.5 pt-2 border-t border-white/[0.06]">
          <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Health Assessment Factors</span>
          <div className="grid grid-cols-1 gap-1 text-[11px] font-mono">
            {healthScore.factors.map((factor, idx) => (
              <div key={idx} className="flex items-center gap-1.5 text-foreground/80">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-blue shrink-0" />
                <span>{factor}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Executive Cost Intelligence Summary */}
      <div className="lg:col-span-7 p-5 rounded-xl border border-white/[0.08] bg-bg-surface space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-semibold text-foreground">Executive Cost Intelligence Summary</h3>
          </div>
          <span className="text-[11px] font-mono text-muted-foreground bg-white/5 px-2 py-0.5 rounded border border-white/10">
            Deterministic Local Intelligence
          </span>
        </div>

        {executiveSummary && executiveSummary.summary_statements && (
          <div className="space-y-2.5">
            {executiveSummary.summary_statements.map((stmt, idx) => (
              <div key={idx} className="p-3 rounded-lg border border-white/[0.05] bg-slate-900/50 flex items-start gap-2.5 text-xs text-foreground/90">
                <Info className="w-4 h-4 text-brand-blue shrink-0 mt-0.5" />
                <span className="leading-relaxed">{stmt}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
