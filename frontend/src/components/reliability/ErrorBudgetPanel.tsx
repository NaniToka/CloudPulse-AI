import React from 'react';
import { ErrorBudgetOverview } from '../../types/reliability';
import { PieChart, AlertCircle, CheckCircle2, Clock } from 'lucide-react';

interface ErrorBudgetPanelProps {
  budgets: ErrorBudgetOverview[];
}

export const ErrorBudgetPanel: React.FC<ErrorBudgetPanelProps> = ({ budgets }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <PieChart className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Error Budget Consumption & Remaining Balances</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">30-Day Rolling Window (2,592,000s)</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {budgets.map((b) => (
          <div key={b.service_name} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white text-sm">{b.service_name}</span>
              <span className="text-xs font-mono font-bold text-indigo-300">
                SLO: {b.target_slo}%
              </span>
            </div>

            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Total Allowed Downtime:</span>
                <span className="font-mono text-white">{b.total_budget_sec}s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Consumed Downtime:</span>
                <span className="font-mono text-rose-400">{b.consumed_budget_sec}s ({b.consumed_budget_pct}%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Remaining Budget:</span>
                <span className="font-mono font-bold text-emerald-400">{b.remaining_budget_sec}s ({b.remaining_budget_pct}%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Burn Rate Multiplier:</span>
                <span className="font-mono font-bold text-amber-400">{b.burn_rate_multiplier}x</span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  b.remaining_budget_pct < 20 ? 'bg-rose-500' : b.remaining_budget_pct < 50 ? 'bg-amber-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${b.remaining_budget_pct}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
