import React from 'react';
import { AlertTriangle, ArrowUpRight, CheckCircle, ShieldAlert, DollarSign, Activity } from 'lucide-react';
import { ExecutivePriorityItem } from '../../types/executive';

interface Props {
  priorities: ExecutivePriorityItem[];
  onSelectPriority?: (item: ExecutivePriorityItem) => void;
}

export const TopPrioritiesQueue: React.FC<Props> = ({ priorities, onSelectPriority }) => {
  const getDomainIcon = (domain: string) => {
    switch (domain.toUpperCase()) {
      case 'INCIDENT':
        return <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
      case 'SECURITY':
        return <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />;
      case 'FINOPS':
        return <DollarSign className="w-3.5 h-3.5 text-emerald-400" />;
      default:
        return <Activity className="w-3.5 h-3.5 text-indigo-400" />;
    }
  };

  const getPriorityBadge = (level: string) => {
    switch (level) {
      case 'P0':
        return <span className="px-2 py-0.5 bg-rose-500/20 border border-rose-500/40 text-rose-400 font-mono font-bold text-xs rounded">P0</span>;
      case 'P1':
        return <span className="px-2 py-0.5 bg-amber-500/20 border border-amber-500/40 text-amber-400 font-mono font-bold text-xs rounded">P1</span>;
      case 'P2':
        return <span className="px-2 py-0.5 bg-blue-500/20 border border-blue-500/40 text-blue-400 font-mono font-bold text-xs rounded">P2</span>;
      default:
        return <span className="px-2 py-0.5 bg-slate-800 border border-slate-700 text-slate-400 font-mono font-bold text-xs rounded">P3</span>;
    }
  };

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 tracking-tight">Prioritized Action Queue</h3>
          <p className="text-xs text-slate-400">Ranked by severity, financial impact, customer exposure, and age</p>
        </div>
        <span className="text-xs font-mono font-semibold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 border border-indigo-500/30 rounded-md">
          {priorities.length} Active Priorities
        </span>
      </div>

      <div className="space-y-3">
        {priorities.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelectPriority?.(item)}
            className="p-4 bg-slate-950/50 border border-slate-800/60 hover:border-indigo-500/50 rounded-lg transition-all cursor-pointer group"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-2">
              <div className="flex items-center gap-3">
                {getPriorityBadge(item.priority_level)}
                <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 uppercase tracking-wider bg-slate-900 px-2 py-0.5 border border-slate-800 rounded">
                  {getDomainIcon(item.domain)} {item.domain}
                </span>
                <h4 className="text-sm font-bold text-slate-200 group-hover:text-indigo-400 transition-colors">
                  {item.title}
                </h4>
              </div>

              <div className="flex items-center gap-3 self-end md:self-auto">
                <span className="text-xs font-mono font-medium text-slate-400 bg-slate-900 px-2 py-1 border border-slate-800 rounded">
                  Score: <strong className="text-indigo-300">{item.priority_score.toFixed(1)}</strong>
                </span>
                <button
                  id={`priority-action-${item.id}`}
                  className="px-2.5 py-1 bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-semibold rounded flex items-center gap-1 transition-all"
                >
                  Inspect <ArrowUpRight className="w-3 h-3" />
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              {item.description}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] pt-2 border-t border-slate-900">
              <div className="text-slate-400">
                <span className="font-semibold text-slate-300">Resource:</span> {item.affected_resource}
              </div>
              <div className="text-slate-400">
                <span className="font-semibold text-slate-300">Business Impact:</span> {item.business_impact}
              </div>
              <div className="text-indigo-400 font-semibold truncate">
                <span>Action:</span> {item.recommended_action}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
