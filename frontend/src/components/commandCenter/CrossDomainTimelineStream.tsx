import React from 'react';
import { TimelineItem } from '../../types/commandCenter';
import { Clock, Activity, AlertTriangle, Link as LinkIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CrossDomainTimelineStreamProps {
  timeline: TimelineItem[];
}

export const CrossDomainTimelineStream: React.FC<CrossDomainTimelineStreamProps> = ({ timeline }) => {
  const navigate = useNavigate();

  const getSourceRoute = (source: string) => {
    const s = source.toLowerCase();
    if (s.includes('slo')) return '/slo';
    if (s.includes('finops') || s.includes('cost')) return '/finops/governance';
    if (s.includes('security')) return '/security';
    if (s.includes('capacity') || s.includes('k8s')) return '/k8s';
    if (s.includes('incident')) return '/incidents';
    return '/dashboard';
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'MEDIUM':
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Unified Cross-Domain Operational Timeline Stream</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{timeline.length} Chronological Events</span>
      </div>

      <div className="space-y-3">
        {timeline.map((item, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
          >
            <div className="flex items-start gap-3">
              <div className="p-2 bg-slate-900 border border-slate-700 rounded-lg text-indigo-400 shrink-0 mt-0.5">
                <Activity className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-bold text-white">{item.event}</h4>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(item.severity)}`}>
                    {item.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-300">Impact: {item.impact}</p>
                <div className="text-[10px] text-slate-500 font-mono">
                  Service: {item.service} | Source: {item.source}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => navigate(getSourceRoute(item.source))}
                className="flex items-center gap-1 px-3 py-1.5 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded text-xs font-semibold transition-colors"
              >
                <LinkIcon className="w-3.5 h-3.5" /> Source Dashboard
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
