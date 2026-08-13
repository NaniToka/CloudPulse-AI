import React from 'react';
import { ReliabilityRecommendationItem } from '../../types/reliability';
import { Lightbulb, ArrowUpRight, Zap } from 'lucide-react';

interface ReliabilityRecommendationsMatrixProps {
  recommendations: ReliabilityRecommendationItem[];
}

export const ReliabilityRecommendationsMatrix: React.FC<ReliabilityRecommendationsMatrixProps> = ({
  recommendations,
}) => {
  const getPriorityBadge = (priority: string) => {
    switch (priority.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">Actionable SRE Reliability Recommendations</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{recommendations.length} Actionable Items</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex flex-col justify-between space-y-3"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono font-bold text-white text-xs">{rec.service}</span>
                <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold border ${getPriorityBadge(rec.priority)}`}>
                  {rec.priority} PRIORITY
                </span>
              </div>
              <h4 className="text-xs font-bold text-indigo-300 mb-1">{rec.category}: {rec.reason}</h4>
              <p className="text-xs text-slate-300 leading-relaxed font-semibold mt-1">
                Action: {rec.recommended_action}
              </p>
            </div>

            <div className="text-[11px] text-emerald-300 border-t border-slate-700/50 pt-2 font-mono">
              Expected Impact: {rec.expected_reliability_impact}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
