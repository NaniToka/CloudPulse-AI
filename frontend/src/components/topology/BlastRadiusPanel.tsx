import React from 'react';
import { Flame, ShieldAlert, ArrowRight, Activity, AlertTriangle } from 'lucide-react';
import { BlastRadiusAnalysisResponse } from '../../types/topology';

interface BlastRadiusPanelProps {
  blastRadius?: BlastRadiusAnalysisResponse | null;
}

export const BlastRadiusPanel: React.FC<BlastRadiusPanelProps> = ({ blastRadius }) => {
  if (!blastRadius) return null;

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
      default:
        return 'bg-slate-800 text-slate-300';
    }
  };

  return (
    <div className="bg-slate-900 border border-rose-500/30 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Flame className="w-5 h-5 text-rose-400" />
            Blast Radius Analysis: <span className="text-rose-400">{blastRadius.target_node_name}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Topological impact calculation displaying affected microservices, infrastructure nodes, providers, and propagation paths.
          </p>
        </div>

        <div className={`px-3 py-1 rounded-full border text-xs font-bold ${getSeverityBadge(blastRadius.severity)}`}>
          {blastRadius.severity} SEVERITY
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Affected Nodes</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">{blastRadius.affected_node_count}</div>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Affected Services</span>
          <div className="text-2xl font-bold text-amber-400 mt-1">{blastRadius.affected_service_count}</div>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Affected Providers</span>
          <div className="text-2xl font-bold text-indigo-400 mt-1">{blastRadius.affected_providers.join(', ')}</div>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Affected Regions</span>
          <div className="text-2xl font-bold text-sky-400 mt-1">{blastRadius.affected_regions.join(', ')}</div>
        </div>
      </div>

      {/* Directly & Indirectly Affected */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Directly Affected Nodes ({blastRadius.directly_affected_nodes.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {blastRadius.directly_affected_nodes.length === 0 ? (
              <span className="text-xs text-slate-500">None</span>
            ) : (
              blastRadius.directly_affected_nodes.map((node, idx) => (
                <span key={idx} className="px-2.5 py-1 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-semibold rounded-lg">
                  {node}
                </span>
              ))
            )}
          </div>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Indirectly Affected Nodes ({blastRadius.indirectly_affected_nodes.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {blastRadius.indirectly_affected_nodes.length === 0 ? (
              <span className="text-xs text-slate-500">None</span>
            ) : (
              blastRadius.indirectly_affected_nodes.map((node, idx) => (
                <span key={idx} className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold rounded-lg">
                  {node}
                </span>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="mt-5 p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300">
        <span className="font-bold text-rose-400">Mitigation Strategy: </span>
        {blastRadius.recommended_mitigation}
      </div>
    </div>
  );
};
