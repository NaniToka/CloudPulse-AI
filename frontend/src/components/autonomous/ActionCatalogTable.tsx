import React, { useState } from 'react';
import { ActionDefinition } from '../../types/autonomous';
import { Play, Shield, RefreshCw, AlertTriangle, Layers } from 'lucide-react';

interface ActionCatalogTableProps {
  actions: ActionDefinition[];
  onSimulate: (action: ActionDefinition) => void;
}

export const ActionCatalogTable: React.FC<ActionCatalogTableProps> = ({
  actions,
  onSimulate,
}) => {
  const [filterDomain, setFilterDomain] = useState<string>('ALL');

  const domains = ['ALL', 'INCIDENT', 'KUBERNETES', 'FINOPS', 'CAPACITY', 'SECURITY', 'GOVERNANCE'];

  const filteredActions = actions.filter((act) =>
    filterDomain === 'ALL' ? true : act.domain.toUpperCase() === filterDomain
  );

  const getRiskBadge = (risk: string) => {
    switch (risk.toUpperCase()) {
      case 'LOW':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'MEDIUM':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Controlled Action Catalog & Risk Registry</h3>
          <p className="text-xs text-slate-400">
            Registered remediation actions with explicit risk classification, permissions, and simulation support.
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-lg border border-slate-700 overflow-x-auto">
          {domains.map((dom) => (
            <button
              key={dom}
              onClick={() => setFilterDomain(dom)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                filterDomain === dom
                  ? 'bg-emerald-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {dom}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Action Type</th>
              <th className="py-3 px-4">Domain</th>
              <th className="py-3 px-4">Provider</th>
              <th className="py-3 px-4">Risk Level</th>
              <th className="py-3 px-4">Description</th>
              <th className="py-3 px-4">Capabilities</th>
              <th className="py-3 px-4 text-right">Simulation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredActions.map((action) => (
              <tr key={action.action_type} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-3 px-4 font-mono font-bold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  {action.action_type}
                </td>
                <td className="py-3 px-4 font-semibold text-slate-300">{action.domain}</td>
                <td className="py-3 px-4 font-medium text-slate-400">{action.provider}</td>
                <td className="py-3 px-4">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getRiskBadge(
                      action.risk_level
                    )}`}
                  >
                    {action.risk_level}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400 max-w-xs truncate">{action.description}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-1 text-[10px]">
                    {action.supports_dry_run && (
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        DRY_RUN
                      </span>
                    )}
                    {action.supports_rollback && (
                      <span className="px-1.5 py-0.5 rounded bg-blue-950/60 text-blue-300 border border-blue-700/50">
                        ROLLBACK
                      </span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  <button
                    onClick={() => onSimulate(action)}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded text-xs font-semibold transition-colors"
                  >
                    <Play className="w-3 h-3" />
                    Simulate
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
