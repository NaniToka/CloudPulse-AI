import React from 'react';
import { Cloud, Server, Layers } from 'lucide-react';
import { ProviderHealthItem } from '../../types/executive';

interface Props {
  providers: ProviderHealthItem[];
}

export const ProviderHealthGrid: React.FC<Props> = ({ providers }) => {
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'kubernetes':
      case 'k8s':
        return <Server className="w-4 h-4 text-purple-400 shrink-0" />;
      case 'aws':
        return <Cloud className="w-4 h-4 text-amber-400 shrink-0" />;
      case 'azure':
        return <Cloud className="w-4 h-4 text-cyan-400 shrink-0" />;
      case 'gcp':
        return <Cloud className="w-4 h-4 text-sky-400 shrink-0" />;
      default:
        return <Cloud className="w-4 h-4 text-indigo-400 shrink-0" />;
    }
  };

  const getRiskBadge = (risk: string) => {
    const r = risk.toUpperCase();
    if (r === 'LOW') return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">LOW</span>;
    if (r === 'MEDIUM') return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">MED</span>;
    return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">HIGH</span>;
  };

  return (
    <div className="p-6 bg-slate-900/70 border border-slate-800/80 rounded-2xl backdrop-blur-xl shadow-2xl h-full flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            Cloud Provider Posture & Health
          </h3>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          Multi-cloud infrastructure posture across AWS, Azure, GCP, & K8s
        </p>

        {/* Clean, 1-column stack layout so sidebar cards never overlap */}
        <div className="space-y-3">
          {providers.map((p, idx) => (
            <div
              key={idx}
              className="p-3.5 bg-slate-950/80 hover:bg-slate-950 border border-slate-800/80 hover:border-slate-700/80 rounded-xl transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getProviderIcon(p.provider)}
                  <span className="font-bold text-slate-100 text-sm">{p.provider}</span>
                </div>
                <div className="flex items-center gap-2">
                  {getRiskBadge(p.security_risk_level)}
                  <span
                    className={`px-2 py-0.5 text-xs font-mono font-bold rounded-md border ${
                      p.health_score >= 90
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}
                  >
                    {p.health_score}/100
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-1.5 bg-slate-800/90 rounded-full overflow-hidden mb-2.5">
                <div
                  className={`h-full rounded-full transition-all ${
                    p.health_score >= 90 ? 'bg-emerald-500' : 'bg-amber-500'
                  }`}
                  style={{ width: `${p.health_score}%` }}
                />
              </div>

              {/* Detail metrics */}
              <div className="grid grid-cols-3 gap-2 text-[11px] pt-1.5 border-t border-slate-800/60">
                <div>
                  <span className="text-slate-500 block text-[10px] font-medium">Monthly Spend</span>
                  <span className="font-mono font-bold text-slate-200">{formatCurrency(p.monthly_spend)}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] font-medium">Incidents</span>
                  <span className={`font-mono font-bold ${p.active_incidents > 0 ? 'text-rose-400' : 'text-slate-300'}`}>
                    {p.active_incidents}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] font-medium">Services</span>
                  <span className="font-mono font-bold text-slate-300">{p.service_count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
