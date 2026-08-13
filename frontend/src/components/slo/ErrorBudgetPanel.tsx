import React from 'react';
import { ErrorBudget } from '../../types/slo';
import { PieChart, Clock, ShieldCheck, AlertCircle } from 'lucide-react';

interface ErrorBudgetPanelProps {
  budgets: ErrorBudget[];
}

export const ErrorBudgetPanel: React.FC<ErrorBudgetPanelProps> = ({ budgets }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <PieChart className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-white">Error Budget Consumption (30d Rolling Window)</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Active Services: {budgets.length}</span>
      </div>

      <div className="space-y-4">
        {budgets.map((eb) => {
          const isExhausted = eb.status === 'EXHAUSTED';
          const isWarning = eb.status === 'WARNING';

          return (
            <div key={eb.service} className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg space-y-2">
              <div className="flex items-center justify-between text-xs">
                <div className="font-mono font-bold text-white flex items-center gap-2">
                  <span>{eb.service}</span>
                  <span className="text-[10px] text-slate-400 font-normal">Target: {eb.target_slo}%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 font-mono text-[11px]">
                    {eb.consumed_budget_sec}s / {eb.total_budget_sec}s
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      isExhausted
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : isWarning
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {eb.remaining_budget_pct}% REMAINING
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden flex">
                <div
                  className={`h-full transition-all ${
                    isExhausted ? 'bg-rose-500' : isWarning ? 'bg-amber-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${eb.remaining_budget_pct}%` }}
                />
                <div
                  className="h-full bg-rose-950/80"
                  style={{ width: `${eb.consumed_budget_pct}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span>Burn Rate Multiplier: <strong className="text-indigo-400">{eb.burn_rate_multiplier}x</strong></span>
                <span>Window: {eb.window_days} Days</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
