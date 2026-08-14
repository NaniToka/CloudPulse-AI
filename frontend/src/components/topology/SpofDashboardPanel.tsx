import React from 'react';
import { AlertTriangle, ShieldAlert, ArrowUpRight } from 'lucide-react';
import { SpofListResponse } from '../../types/topology';

interface SpofDashboardPanelProps {
  spofData?: SpofListResponse | null;
  onSelectNodeById: (nodeId: string) => void;
}

export const SpofDashboardPanel: React.FC<SpofDashboardPanelProps> = ({
  spofData,
  onSelectNodeById,
}) => {
  if (!spofData || spofData.spofs.length === 0) return null;

  const getRiskBadge = (risk: string) => {
    switch (risk.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-rose-400" />
          Single Points of Failure (SPOF) Detection ({spofData.total_spofs})
        </h2>
        <span className="text-xs text-slate-400">Deterministic topological risk analysis</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {spofData.spofs.map((item) => (
          <div
            key={item.node_id}
            className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-100">{item.node_name}</span>
                <span className={`text-xs px-2.5 py-0.5 rounded border font-semibold ${getRiskBadge(item.risk_level)}`}>
                  {item.risk_level} SPOF
                </span>
              </div>

              <div className="text-xs text-slate-400 mt-1">
                {item.provider} • {item.node_type} • {item.region}
              </div>

              <p className="text-xs text-slate-300 mt-3">{item.reason}</p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-xs text-slate-400">
                Dependents: <span className="text-amber-400 font-bold">{item.dependent_count} services</span>
              </span>

              <button
                onClick={() => onSelectNodeById(item.node_id)}
                className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium transition"
              >
                Focus Node <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
