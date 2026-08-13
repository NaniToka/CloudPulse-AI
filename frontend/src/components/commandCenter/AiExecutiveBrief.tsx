import React from 'react';
import { ExecutiveBrief } from '../../types/commandCenter';
import { Sparkles, Bot, AlertTriangle, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface AiExecutiveBriefProps {
  brief: ExecutiveBrief | null;
}

export const AiExecutiveBrief: React.FC<AiExecutiveBriefProps> = ({ brief }) => {
  if (!brief) return null;

  return (
    <div className="bg-slate-900/80 border border-indigo-500/30 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4 relative overflow-hidden">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-indigo-500/15 border border-indigo-500/30 rounded-lg text-indigo-400">
            <Bot className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">AI Executive Brief — What Needs Attention Right Now?</h3>
            <p className="text-xs text-slate-400">Synthesized 5-point operational intelligence analysis.</p>
          </div>
        </div>

        <span
          className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${
            brief.is_ai_powered
              ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          {brief.badge}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Summary */}
        <div className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg space-y-1">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">1. What is happening?</div>
          <p className="text-xs text-slate-200 leading-relaxed font-medium">{brief.summary}</p>
        </div>

        {/* 2. Top Concern */}
        <div className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg space-y-1">
          <div className="text-[11px] font-bold text-amber-400 uppercase tracking-wider">2. Top Concern</div>
          <p className="text-xs text-amber-200 font-semibold leading-relaxed">{brief.top_concern}</p>
        </div>

        {/* 3. Business Impact */}
        <div className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg space-y-1">
          <div className="text-[11px] font-bold text-rose-400 uppercase tracking-wider">3. Business Impact</div>
          <p className="text-xs text-rose-200 leading-relaxed font-medium">{brief.business_impact}</p>
        </div>

        {/* 4. Recommended Action */}
        <div className="p-3.5 bg-indigo-950/40 border border-indigo-600/40 rounded-lg space-y-1">
          <div className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider">4. Recommended Next Action</div>
          <p className="text-xs text-indigo-100 font-semibold leading-relaxed">{brief.recommended_action}</p>
        </div>
      </div>
    </div>
  );
};
