import React from "react";
import { DollarSign, AlertTriangle, ShieldCheck, PieChart, Plus } from "lucide-react";
import type { CostBudgetItem } from "@/types/cost";

interface FinOpsBudgetPanelProps {
  budgets: CostBudgetItem[];
  onAddBudget?: () => void;
}

export default function FinOpsBudgetPanel({ budgets, onAddBudget }: FinOpsBudgetPanelProps) {
  const getStatusBadge = (status: string, utilizationPct: number) => {
    if (utilizationPct >= 100) {
      return <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-rose-500/20 text-rose-300 border border-rose-500/30">EXCEEDED (100%)</span>;
    }
    if (utilizationPct >= 90) {
      return <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">CRITICAL (90%)</span>;
    }
    if (utilizationPct >= 75) {
      return <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">WARNING (75%)</span>;
    }
    return <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">HEALTHY</span>;
  };

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <PieChart className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-semibold text-foreground">Budget Intelligence & Allocation</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">
          {budgets.length} Active Budgets Tracked
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {budgets.map((b) => {
          const util = Math.min(100, Math.max(0, b.utilization_pct));
          const isHigh = util >= 90;
          return (
            <div
              key={b.id}
              className="p-4 rounded-lg border border-white/5 bg-black/20 hover:border-white/10 transition-colors space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="text-xs font-semibold text-foreground">{b.name}</h4>
                  <p className="text-[11px] text-muted-foreground font-mono">
                    Provider: {b.provider.toUpperCase()} | Env: {b.environment}
                  </p>
                </div>
                {getStatusBadge(b.threshold_status, b.utilization_pct)}
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-muted-foreground">
                    Spent: <strong className="text-foreground">${b.current_spend.toLocaleString()}</strong> / ${b.amount.toLocaleString()}
                  </span>
                  <span className="text-foreground font-semibold">{b.utilization_pct}%</span>
                </div>

                {/* Progress bar with threshold markers */}
                <div className="relative h-2 w-full bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isHigh ? "bg-gradient-to-r from-amber-500 to-rose-500" : "bg-gradient-to-r from-blue-500 to-indigo-500"
                    }`}
                    style={{ width: `${util}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-[10px] text-muted-foreground font-mono pt-1">
                  <span>Thresholds: 50% | 75% | 90% | 100%</span>
                  <span>Proj: ${b.projected_spend.toLocaleString()}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
