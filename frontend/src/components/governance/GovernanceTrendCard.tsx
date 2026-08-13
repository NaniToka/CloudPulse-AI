import React from "react";
import { TrendingUp, Calendar } from "lucide-react";
import type { GovernanceTrendResponse } from "@/types/governance";

interface GovernanceTrendCardProps {
  trends: GovernanceTrendResponse | null;
  selectedDays: number;
  onDaysChange: (days: number) => void;
}

export default function GovernanceTrendCard({ trends, selectedDays, onDaysChange }: GovernanceTrendCardProps) {
  if (!trends) return null;

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold text-foreground">Compliance Score & Violation Trends</h3>
        </div>

        <div className="flex items-center gap-1 text-xs">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => onDaysChange(d)}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold border transition-colors ${
                selectedDays === d
                  ? "bg-brand-blue text-white border-brand-blue"
                  : "bg-black/30 border-white/10 text-muted-foreground hover:bg-white/5"
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {trends.compliance_trend.map((pt, idx) => (
          <div key={idx} className="p-3 rounded-lg border border-white/5 bg-black/20 text-center space-y-1">
            <span className="text-[11px] text-muted-foreground block">{pt.day}</span>
            <span className="text-lg font-bold text-emerald-400 block">{pt.score.toFixed(1)}%</span>
            <span className="text-[10px] text-amber-300 block">{pt.violations} Open Violations</span>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground pt-1 border-t border-white/5">
        <span>Resolved Violations ({trends.horizon_days}d): <strong className="text-emerald-400">{trends.resolved_violations_period}</strong></span>
        <span>Policy Coverage: <strong className="text-foreground">{trends.policy_coverage_percentage}%</strong></span>
      </div>
    </div>
  );
}
