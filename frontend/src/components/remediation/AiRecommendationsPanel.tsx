import React from 'react';
import { Bot, Sparkles, AlertTriangle, ShieldCheck, Play, Eye } from 'lucide-react';
import { RemediationAnalyzeResult } from '../../types/remediation';

interface AiRecommendationsPanelProps {
  analysis: RemediationAnalyzeResult | null;
  onSelectAction?: (action: any) => void;
}

export const AiRecommendationsPanel: React.FC<AiRecommendationsPanelProps> = ({
  analysis,
  onSelectAction,
}) => {
  if (!analysis) return null;

  return (
    <div className="bg-slate-900/80 border border-indigo-500/30 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-indigo-400 animate-pulse" />
          <h3 className="text-base font-bold text-white">AIOps Remediation Intelligence Brief</h3>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${
            analysis.is_ai_powered
              ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          {analysis.badge}
        </span>
      </div>

      <p className="text-xs text-slate-200 leading-relaxed font-medium">{analysis.executive_summary}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        {analysis.recommended_actions.map((act, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-800/60 border border-slate-700 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white">{act.resource || 'payment-service'}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                {act.risk_level} RISK
              </span>
            </div>

            <div className="text-indigo-300 font-bold font-mono">{act.action_type}</div>
            <p className="text-slate-300">{act.reason}</p>

            <div className="flex items-center justify-between pt-2 border-t border-slate-700/60 text-[11px]">
              <span className="text-slate-400">Human Approval Required: <strong className="text-white">YES</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
