import React from 'react';
import { TrendingUp, TrendingDown, Minus, ArrowUpRight } from 'lucide-react';
import { OperationalTrendItem } from '../../types/executive';

interface Props {
  trends: OperationalTrendItem[];
}

export const OperationalTrendsChart: React.FC<Props> = ({ trends }) => {
  const getTrendBadge = (status: string, direction: string) => {
    switch (status) {
      case 'IMPROVING':
        return <span className="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold rounded flex items-center gap-1"><TrendingDown className="w-3.5 h-3.5" /> IMPROVING</span>;
      case 'WORSENING':
        return <span className="px-2.5 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold rounded flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5" /> WORSENING</span>;
      default:
        return <span className="px-2.5 py-1 bg-slate-800 border border-slate-700 text-slate-300 text-xs font-semibold rounded flex items-center gap-1"><Minus className="w-3.5 h-3.5" /> STABLE</span>;
    }
  };

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">Operational Trends (MoM Comparison)</h3>
      <p className="text-xs text-slate-400 mb-4">Period-over-period direction and rate-of-change across operational metrics</p>

      <div className="space-y-3">
        {trends.map((t, idx) => (
          <div key={idx} className="p-3.5 bg-slate-950/40 border border-slate-800/50 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 border border-indigo-500/20 rounded">
                  {t.domain}
                </span>
                <span className="text-sm font-bold text-slate-200">{t.metric_name}</span>
              </div>
              <div className="text-xs text-slate-400 flex items-center gap-4">
                <span>Current: <strong className="text-slate-200">{t.current_period} {t.unit}</strong></span>
                <span>Prev: <strong className="text-slate-400">{t.previous_period} {t.unit}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-3 self-end sm:self-auto">
              <span className={`text-xs font-mono font-bold ${t.percentage_change < 0 ? 'text-emerald-400' : 'text-slate-300'}`}>
                {t.percentage_change > 0 ? `+${t.percentage_change}%` : `${t.percentage_change}%`}
              </span>
              {getTrendBadge(t.trend_status, t.direction)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
