import React from 'react';
import { Cloud, Server, Shield, Activity, DollarSign } from 'lucide-react';
import { ProviderHealthItem } from '../../types/executive';

interface Props {
  providers: ProviderHealthItem[];
}

export const ProviderHealthGrid: React.FC<Props> = ({ providers }) => {
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">Cloud Provider Posture & Health</h3>
      <p className="text-xs text-slate-400 mb-4">Multi-cloud infrastructure status across AWS, Azure, GCP, and Kubernetes</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {providers.map((p, idx) => (
          <div key={idx} className="p-4 bg-slate-950/60 border border-slate-800/70 hover:border-slate-700/80 rounded-lg transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {p.provider.toLowerCase() === 'kubernetes' ? (
                  <Server className="w-5 h-5 text-indigo-400" />
                ) : (
                  <Cloud className="w-5 h-5 text-sky-400" />
                )}
                <span className="font-bold text-slate-200 text-sm">{p.provider}</span>
              </div>
              <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded ${
                p.health_score >= 90 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
              }`}>
                {p.health_score}/100
              </span>
            </div>

            <div className="space-y-2 text-xs mb-3">
              <div className="flex items-center justify-between text-slate-400">
                <span>Monthly Spend:</span>
                <span className="font-mono font-semibold text-slate-200">{formatCurrency(p.monthly_spend)}</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Active Incidents:</span>
                <span className={`font-mono font-semibold ${p.active_incidents > 0 ? 'text-rose-400' : 'text-slate-300'}`}>{p.active_incidents}</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Security Risk:</span>
                <span className="font-semibold text-slate-300">{p.security_risk_level}</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Services Tracked:</span>
                <span className="font-mono font-semibold text-slate-300">{p.service_count}</span>
              </div>
            </div>

            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500" style={{ width: `${p.health_score}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
