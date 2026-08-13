import React from 'react';
import { TopOpportunityItem } from '../../types/commandCenter';
import { Lightbulb, PiggyBank, ArrowUpRight, Zap } from 'lucide-react';

interface TopOpportunitiesPanelProps {
  opportunities: TopOpportunityItem[];
}

export const TopOpportunitiesPanel: React.FC<TopOpportunitiesPanelProps> = ({ opportunities }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">Top Cross-Domain Opportunities</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Optimization Matrix</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {opportunities.map((opp) => (
          <div
            key={opp.id}
            className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex flex-col justify-between space-y-3"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {opp.source}
                </span>
                {opp.potential_savings_monthly && (
                  <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1">
                    <PiggyBank className="w-3.5 h-3.5" /> ${opp.potential_savings_monthly.toLocaleString()}/mo
                  </span>
                )}
              </div>
              <h4 className="text-xs font-bold text-white mb-1">{opp.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed">{opp.recommended_action}</p>
            </div>

            <div className="flex items-center justify-between text-[11px] border-t border-slate-700/50 pt-2 text-slate-400">
              <span>Impact: <strong className="text-slate-200">{opp.impact}</strong></span>
              <span className="font-bold text-indigo-400 uppercase">{opp.priority} PRIORITY</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
