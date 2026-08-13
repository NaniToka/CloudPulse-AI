import React from 'react';
import { TopRiskItem } from '../../types/commandCenter';
import { Flame, ShieldAlert, ArrowRight } from 'lucide-react';

interface TopRisksRankingProps {
  risks: TopRiskItem[];
}

export const TopRisksRanking: React.FC<TopRisksRankingProps> = ({ risks }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'border-rose-500/40 bg-rose-950/20 text-rose-300';
      case 'HIGH':
        return 'border-amber-500/40 bg-amber-950/20 text-amber-300';
      case 'MEDIUM':
      default:
        return 'border-blue-500/40 bg-blue-950/20 text-blue-300';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-amber-400 animate-pulse" />
          <h3 className="text-base font-bold text-white">Top 5 Enterprise Operational Risks</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Deterministic Risk Rank</span>
      </div>

      <div className="space-y-3">
        {risks.map((r) => {
          const colorClass = getSeverityColor(r.severity);

          return (
            <div
              key={r.rank}
              className={`p-4 rounded-xl border ${colorClass} flex flex-col md:flex-row items-start md:items-center justify-between gap-4`}
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-900/80 border border-slate-700 flex items-center justify-center font-mono font-extrabold text-white text-sm shrink-0">
                  #{r.rank}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-bold text-white">{r.title}</h4>
                    <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-900/80">
                      {r.severity} ({r.score} pts)
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{r.reason}</p>
                  <div className="text-[11px] text-amber-300">Impact: {r.impact}</div>
                </div>
              </div>

              <div className="flex flex-col items-end gap-1 whitespace-nowrap shrink-0">
                <span className="text-[10px] text-slate-400 font-mono font-bold">Service: {r.affected_service}</span>
                <span className="px-3 py-1 bg-slate-900/80 border border-slate-700 rounded text-xs font-semibold text-slate-200">
                  Action: {r.recommended_action}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
