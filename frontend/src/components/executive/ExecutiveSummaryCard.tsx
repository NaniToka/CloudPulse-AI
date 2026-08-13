import React from 'react';
import { Sparkles, Bot, Clock, CheckCircle2 } from 'lucide-react';
import { ExecutiveSummaryResponse } from '../../types/executive';

interface Props {
  summary: ExecutiveSummaryResponse;
  onRefresh?: () => void;
}

export const ExecutiveSummaryCard: React.FC<Props> = ({ summary, onRefresh }) => {
  return (
    <div className="p-6 bg-gradient-to-br from-indigo-950/40 via-slate-900/90 to-slate-900/80 border border-indigo-500/20 rounded-xl backdrop-blur-md shadow-xl relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 tracking-tight">Executive Briefing & Synthesis</h3>
            <span className="text-[11px] text-indigo-400 font-medium flex items-center gap-1">
              <Bot className="w-3 h-3" /> {summary.source}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
            <Clock className="w-3 h-3" /> {new Date(summary.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          {onRefresh && (
            <button
              id="refresh-summary-btn"
              onClick={onRefresh}
              className="px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 rounded-md transition-all"
            >
              Refresh
            </button>
          )}
        </div>
      </div>

      <p className="text-sm text-slate-200 leading-relaxed mb-4 bg-slate-950/40 p-4 border border-slate-800/60 rounded-lg">
        {summary.summary_text}
      </p>

      {summary.key_highlights && summary.key_highlights.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {summary.key_highlights.map((highlight, idx) => (
            <div key={idx} className="flex items-start gap-2 text-xs text-slate-300 bg-slate-900/60 p-2.5 border border-slate-800/40 rounded-md">
              <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <span>{highlight}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
