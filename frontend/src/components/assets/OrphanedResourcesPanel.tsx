import React from 'react';
import { AlertTriangle, DollarSign, ArrowUpRight, ShieldAlert } from 'lucide-react';
import { OrphanedResourcesResponse } from '../../types/assets';

interface OrphanedResourcesPanelProps {
  orphanedData?: OrphanedResourcesResponse | null;
  onSelectResourceById: (id: string) => void;
}

export const OrphanedResourcesPanel: React.FC<OrphanedResourcesPanelProps> = ({
  orphanedData,
  onSelectResourceById,
}) => {
  if (!orphanedData || orphanedData.orphaned_resources.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-amber-500/30 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Orphaned & Unutilized Resource Recommendations ({orphanedData.total_orphaned})
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Detect unattached storage volumes, idle compute instances, and unmapped cloud assets to prevent waste.
          </p>
        </div>

        <div className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-lg">
          <DollarSign className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-semibold text-amber-300">
            Potential Monthly Savings: ${orphanedData.total_potential_savings.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {orphanedData.orphaned_resources.map((item) => (
          <div
            key={item.resource_id}
            className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-100">{item.resource_name}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  {item.provider} • {item.region}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-2">{item.reason}</p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <div className="text-xs text-slate-300">
                <span>Cost: </span>
                <span className="line-through text-slate-500">${item.monthly_cost}</span>
                <span className="text-emerald-400 font-bold ml-1.5">+${item.potential_savings} savings</span>
              </div>

              <button
                onClick={() => onSelectResourceById(item.resource_id)}
                className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium transition"
              >
                Inspect & Remediate <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
