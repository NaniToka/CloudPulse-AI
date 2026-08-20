import React from 'react';
import { TopOpportunityItem } from '../../types/commandCenter';
import { Lightbulb, PiggyBank, ArrowUpRight, Zap } from 'lucide-react';

interface TopOpportunitiesPanelProps {
  opportunities: TopOpportunityItem[];
}

export const TopOpportunitiesPanel: React.FC<TopOpportunitiesPanelProps> = ({ opportunities }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-xl space-y-4 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Lightbulb className="w-4 h-4" />
          </div>
          <h3 className="text-base font-bold text-white tracking-tight">Top Cross-Domain Opportunities</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold bg-slate-800/80 px-2.5 py-1 rounded-full border border-slate-700/80">
          Optimization Matrix
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {opportunities.map((opp) => (
          <div
            key={opp.id}
            className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-emerald-500/40 flex flex-col justify-between space-y-3 transition-all duration-200"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {opp.source}
                </span>
                {opp.potential_savings_monthly && (
                  <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1">
                    <PiggyBank className="w-3.5 h-3.5" /> ${opp.potential_savings_monthly.toLocaleString()}/mo
                  </span>
                )}
              </div>
              <h4 className="text-xs font-bold text-white mb-1 leading-snug">{opp.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed">{opp.recommended_action}</p>
            </div>

            <div className="flex items-center justify-between text-[11px] border-t border-slate-800/80 pt-2 text-slate-400">
              <span className="truncate">Impact: <strong className="text-slate-200">{opp.impact}</strong></span>
              <span className="font-bold text-indigo-400 uppercase shrink-0">{opp.priority} PRIORITY</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
