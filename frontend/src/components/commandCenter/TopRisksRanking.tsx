import React from 'react';
import { TopRiskItem } from '../../types/commandCenter';
import { Flame, ShieldAlert, ArrowRight, Activity } from 'lucide-react';

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
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-xl space-y-4 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Flame className="w-4 h-4 animate-pulse" />
          </div>
          <h3 className="text-base font-bold text-white tracking-tight">Top 5 Operational Risks</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold bg-slate-800/80 px-2.5 py-1 rounded-full border border-slate-700/80">
          Deterministic Risk Rank
        </span>
      </div>

      <div className="space-y-3">
        {risks.map((r) => {
          const colorClass = getSeverityColor(r.severity);

          return (
            <div
              key={r.rank}
              className={`p-4 rounded-xl border ${colorClass} transition-all duration-200 hover:border-slate-600 relative overflow-hidden flex flex-col space-y-3`}
            >
              {/* Top row: Rank, Title, Severity Badge, Service */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 min-w-0">
                  <div className="w-7 h-7 rounded-lg bg-slate-900/90 border border-slate-700/80 flex items-center justify-center font-mono font-extrabold text-white text-xs shrink-0 shadow-md">
                    #{r.rank}
                  </div>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="text-xs font-bold text-white truncate">{r.title}</h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-900/90 border border-slate-800 shrink-0">
                        {r.severity} ({r.score} PTS)
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed mt-1">{r.reason}</p>
                  </div>
                </div>

                <div className="text-[10px] font-mono font-bold text-slate-400 shrink-0 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                  {r.affected_service}
                </div>
              </div>

              {/* Bottom row: Impact and Action tag */}
              <div className="pt-2 border-t border-slate-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <div className="text-[11px] text-amber-300 font-medium truncate">
                  <strong className="text-amber-400">Impact:</strong> {r.impact}
                </div>
                <div className="px-2.5 py-1 bg-slate-900/90 border border-slate-700/80 rounded-lg text-[11px] font-semibold text-slate-200 truncate max-w-full sm:max-w-[320px]">
                  <strong className="text-indigo-400">Action:</strong> {r.recommended_action}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
