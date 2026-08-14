import React from 'react';
import { Cloud, PieChart, ShieldCheck } from 'lucide-react';
import { AssetProviderStat } from '../../types/assets';

interface AssetProviderDistributionProps {
  providers: AssetProviderStat[];
}

export const AssetProviderDistribution: React.FC<AssetProviderDistributionProps> = ({ providers }) => {
  const getProviderColor = (provider: string) => {
    switch (provider.toUpperCase()) {
      case 'AWS':
        return { bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400', bar: 'bg-amber-500' };
      case 'AZURE':
        return { bg: 'bg-sky-500/10', border: 'border-sky-500/30', text: 'text-sky-400', bar: 'bg-sky-500' };
      case 'GCP':
        return { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', bar: 'bg-emerald-500' };
      case 'KUBERNETES':
        return { bg: 'bg-indigo-500/10', border: 'border-indigo-500/30', text: 'text-indigo-400', bar: 'bg-indigo-500' };
      default:
        return { bg: 'bg-slate-800', border: 'border-slate-700', text: 'text-slate-300', bar: 'bg-slate-600' };
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Cloud className="w-5 h-5 text-indigo-400" />
          Multi-Cloud Provider Inventory & Cost Distribution
        </h2>
        <span className="text-xs text-slate-400">AWS • Azure • GCP • Kubernetes</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {providers.map((p) => {
          const style = getProviderColor(p.provider);
          return (
            <div key={p.provider} className={`p-4 rounded-xl border ${style.bg} ${style.border} transition`}>
              <div className="flex items-center justify-between">
                <span className={`text-sm font-bold ${style.text}`}>{p.provider}</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-900/80 text-slate-300">
                  {p.percentage}% share
                </span>
              </div>

              <div className="mt-3 flex items-baseline justify-between">
                <span className="text-2xl font-bold text-slate-100">{p.resource_count}</span>
                <span className="text-xs font-medium text-slate-400">resources</span>
              </div>

              <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                <span>Monthly Burn:</span>
                <span className="font-semibold text-slate-200">${p.monthly_cost.toLocaleString()}</span>
              </div>

              {/* Progress bar */}
              <div className="mt-3 w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                <div className={`h-full ${style.bar}`} style={{ width: `${p.percentage}%` }} />
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  Health Score
                </span>
                <span className="font-bold text-slate-200">{p.health_score}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
