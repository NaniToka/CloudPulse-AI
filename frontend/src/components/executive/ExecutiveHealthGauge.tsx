import React from 'react';
import { Activity, ShieldCheck, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { HealthScoreResponse } from '../../types/executive';

interface Props {
  health: HealthScoreResponse;
}

export const ExecutiveHealthGauge: React.FC<Props> = ({ health }) => {
  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'HEALTHY':
        return <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold rounded-full flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5" /> HEALTHY</span>;
      case 'LOW_RISK':
        return <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold rounded-full flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5" /> LOW RISK</span>;
      case 'MODERATE_RISK':
        return <span className="px-3 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold rounded-full flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> MODERATE RISK</span>;
      default:
        return <span className="px-3 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold rounded-full flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> HIGH RISK</span>;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
    if (score >= 75) return 'text-blue-400 border-blue-500/40 bg-blue-500/10';
    if (score >= 60) return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/40 bg-rose-500/10';
  };

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-800/60">
        <div className="flex items-center gap-6">
          <div className={`w-24 h-24 rounded-full border-4 flex flex-col items-center justify-center font-bold shadow-lg transition-all ${getScoreColor(health.overall_score)}`}>
            <span className="text-3xl tracking-tight">{health.overall_score}</span>
            <span className="text-[10px] uppercase font-medium tracking-wider text-slate-400">/ 100</span>
          </div>

          <div>
            <div className="flex items-center gap-3 mb-1.5">
              <h2 className="text-xl font-bold text-slate-100 tracking-tight">Cloud Operations Health Score</h2>
              {getRiskBadge(health.risk_level)}
            </div>
            <p className="text-xs text-slate-400 max-w-xl leading-relaxed">
              {health.explanation}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-slate-950/60 border border-slate-800/80 px-4 py-3 rounded-lg self-start md:self-auto">
          <Activity className="w-5 h-5 text-indigo-400" />
          <div>
            <span className="text-[11px] text-slate-400 uppercase tracking-wider block font-medium">Posture Trend</span>
            <span className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" /> {health.trend}
            </span>
          </div>
        </div>
      </div>

      {/* Component Breakdown Progress Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-6">
        {health.components.map((comp, idx) => (
          <div key={idx} className="p-3.5 bg-slate-950/40 border border-slate-800/50 rounded-lg hover:border-slate-700/80 transition-all">
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="font-semibold text-slate-300">{comp.name}</span>
              <span className="font-bold text-slate-100">{comp.score}/100</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mb-2">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  comp.score >= 80 ? 'bg-emerald-500' : comp.score >= 65 ? 'bg-amber-500' : 'bg-rose-500'
                }`}
                style={{ width: `${comp.score}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 truncate max-w-[200px]">{comp.details}</span>
              <span className="text-[10px] font-mono text-indigo-400">{comp.weight_pct}% wt</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
