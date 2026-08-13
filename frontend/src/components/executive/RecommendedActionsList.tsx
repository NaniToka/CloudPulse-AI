import React from 'react';
import { ArrowUpRight, DollarSign, ShieldAlert, Wrench } from 'lucide-react';
import { ExecutiveRecommendationItem } from '../../types/executive';

interface Props {
  recommendations: ExecutiveRecommendationItem[];
}

export const RecommendedActionsList: React.FC<Props> = ({ recommendations }) => {
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">Executive Engineering Recommendations</h3>
      <p className="text-xs text-slate-400 mb-4">High-ROI recommendations synthesized from cross-domain telemetry and FinOps governance</p>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="p-3.5 bg-slate-950/40 border border-slate-800/50 hover:border-slate-700/80 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 border border-emerald-500/20 rounded">
                  {rec.domain}
                </span>
                <h4 className="text-sm font-bold text-slate-200">{rec.title}</h4>
              </div>
              <div className="text-xs text-slate-400">
                <span>Owner: <strong className="text-slate-300">{rec.suggested_owner}</strong></span> | <span>Impact: <strong className="text-indigo-300">{rec.impact}</strong></span>
                {rec.estimated_savings > 0 && (
                  <span className="ml-2 text-emerald-400 font-mono font-semibold">
                    (Est. Savings: {formatCurrency(rec.estimated_savings)}/mo)
                  </span>
                )}
              </div>
            </div>

            <button
              id={`rec-action-${rec.id}`}
              className="px-3 py-1.5 bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-semibold rounded flex items-center gap-1 self-end sm:self-auto transition-all"
            >
              {rec.action} <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
