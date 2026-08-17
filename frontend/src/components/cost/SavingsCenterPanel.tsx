import React from "react";
import { PiggyBank, Sparkles, TrendingDown, DollarSign } from "lucide-react";
import type { SavingsCenterResponse } from "@/types/cost";

interface SavingsCenterPanelProps {
  savingsCenter: SavingsCenterResponse | null;
}

export default function SavingsCenterPanel({ savingsCenter }: SavingsCenterPanelProps) {
  if (!savingsCenter) return null;

  return (
    <div className="p-5 rounded-xl border border-white/[0.08] bg-bg-surface space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <PiggyBank className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold text-foreground">Savings Center</h3>
        </div>
        <span className="text-xs text-emerald-400 font-mono flex items-center gap-1 font-semibold">
          <Sparkles className="w-3.5 h-3.5" /> {savingsCenter.opportunity_count} Active Opportunities
        </span>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg border border-emerald-500/20 bg-emerald-500/5 space-y-1">
          <span className="text-xs text-emerald-300 font-mono">Potential Monthly Savings</span>
          <div className="text-xl font-bold font-mono text-emerald-400">
            ${savingsCenter.total_monthly_savings.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className="p-4 rounded-lg border border-brand-blue/20 bg-brand-blue/5 space-y-1">
          <span className="text-xs text-brand-blue font-mono">Potential Annual Savings</span>
          <div className="text-xl font-bold font-mono text-foreground">
            ${savingsCenter.total_annual_savings.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
          <span className="text-[10px] text-muted-foreground block font-mono">Monthly × 12 Deterministic Extrapolation</span>
        </div>

        <div className="p-4 rounded-lg border border-white/[0.06] bg-slate-900/60 space-y-1">
          <span className="text-xs text-muted-foreground font-mono">Active Opportunities</span>
          <div className="text-xl font-bold font-mono text-foreground">{savingsCenter.opportunity_count}</div>
        </div>

        <div className="p-4 rounded-lg border border-white/[0.06] bg-slate-900/60 space-y-1">
          <span className="text-xs text-muted-foreground font-mono">Avg Savings / Opportunity</span>
          <div className="text-xl font-bold font-mono text-foreground">
            ${savingsCenter.average_savings_per_opportunity.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        {/* By Category */}
        <div className="p-3.5 rounded-lg border border-white/[0.05] bg-slate-900/40 space-y-2">
          <span className="text-xs font-semibold text-muted-foreground">Savings by Recommendation Type</span>
          <div className="space-y-2">
            {savingsCenter.by_category.map((item, idx) => (
              <div key={idx} className="space-y-1 font-mono text-xs">
                <div className="flex justify-between text-foreground">
                  <span className="capitalize">{item.category.replace("_", " ")}</span>
                  <span className="font-semibold text-emerald-400">${item.savings.toLocaleString()}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 rounded-full"
                    style={{
                      width: `${savingsCenter.total_monthly_savings > 0 ? (item.savings / savingsCenter.total_monthly_savings) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* By Provider */}
        <div className="p-3.5 rounded-lg border border-white/[0.05] bg-slate-900/40 space-y-2">
          <span className="text-xs font-semibold text-muted-foreground">Savings by Cloud Provider</span>
          <div className="space-y-2">
            {savingsCenter.by_provider.map((item, idx) => (
              <div key={idx} className="space-y-1 font-mono text-xs">
                <div className="flex justify-between text-foreground">
                  <span>{item.provider}</span>
                  <span className="font-semibold text-brand-blue">${item.savings.toLocaleString()}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-brand-blue rounded-full"
                    style={{
                      width: `${savingsCenter.total_monthly_savings > 0 ? (item.savings / savingsCenter.total_monthly_savings) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
