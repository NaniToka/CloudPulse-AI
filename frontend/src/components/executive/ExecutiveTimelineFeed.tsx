import React from 'react';
import { Clock, Activity, ShieldCheck, AlertCircle, CheckCircle2 } from 'lucide-react';
import { ExecutiveTimelineEvent } from '../../types/executive';

interface Props {
  events: ExecutiveTimelineEvent[];
}

export const ExecutiveTimelineFeed: React.FC<Props> = ({ events }) => {
  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">Executive Timeline Feed</h3>
      <p className="text-xs text-slate-400 mb-4">Unified cross-domain event feed across Incidents, FinOps, Security, and Governance</p>

      <div className="space-y-4">
        {events.map((evt) => (
          <div key={evt.id} className="relative pl-6 border-l-2 border-slate-800 hover:border-indigo-500/60 transition-colors py-1">
            <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-slate-900 border-2 border-indigo-500 flex items-center justify-center">
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            </div>

            <div className="flex items-center justify-between gap-2 mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-indigo-400 uppercase bg-indigo-500/10 px-2 py-0.5 border border-indigo-500/20 rounded">
                  {evt.domain}
                </span>
                <h4 className="text-sm font-bold text-slate-200">{evt.title}</h4>
              </div>
              <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">{evt.details}</p>
            <div className="text-[11px] text-slate-400 mt-1 font-mono">Resource: {evt.resource}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
