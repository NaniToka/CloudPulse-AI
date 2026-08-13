import React from 'react';
import { SloRecommendation } from '../../types/slo';
import { Lightbulb, ArrowUpRight, Zap, CheckCircle2 } from 'lucide-react';

interface ReliabilityRecommendationsPanelProps {
  recommendations: SloRecommendation[];
}

export const ReliabilityRecommendationsPanel: React.FC<ReliabilityRecommendationsPanelProps> = ({
  recommendations,
}) => {
  const getPriorityBadge = (priority: string) => {
    switch (priority.toUpperCase()) {
      case 'HIGH':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'MEDIUM':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'LOW':
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-semibold text-white">Recommended Reliability Recovery Actions</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">AI SRE Recommendations</span>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
          >
            <div className="space-y-1 max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-white text-xs">{rec.service}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getPriorityBadge(rec.priority)}`}>
                  {rec.priority} PRIORITY
                </span>
              </div>
              <div className="text-xs font-semibold text-amber-300">{rec.problem}</div>
              <p className="text-xs text-slate-300 leading-relaxed">{rec.recommendation}</p>
              <div className="text-[11px] text-slate-400">Impact: {rec.impact}</div>
            </div>

            <div className="flex flex-col items-end gap-2 whitespace-nowrap">
              <div className="px-3 py-1.5 bg-emerald-950/60 border border-emerald-600/40 rounded-lg text-emerald-300 text-xs font-semibold">
                ✨ {rec.expected_improvement}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
