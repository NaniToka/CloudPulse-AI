import React from 'react';
import {
  Server,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  ShieldAlert,
  Activity,
  CheckCircle2,
  AlertTriangle,
  FileText,
} from 'lucide-react';
import { TopologyNodeItem } from '../../types/topology';

interface TopologyResourcePanelProps {
  node?: TopologyNodeItem | null;
  upstreamNodes: TopologyNodeItem[];
  downstreamNodes: TopologyNodeItem[];
  onSelectNode: (node: TopologyNodeItem) => void;
  onCalculateBlastRadius: (nodeId: string) => void;
}

export const TopologyResourcePanel: React.FC<TopologyResourcePanelProps> = ({
  node,
  upstreamNodes,
  downstreamNodes,
  onSelectNode,
  onCalculateBlastRadius,
}) => {
  if (!node) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6 text-center text-slate-500 text-sm">
        Select any node in the topology canvas to inspect identity, dependencies, security posture, and blast radius.
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">{node.name}</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {node.provider} • {node.type} • {node.region} • {node.environment}
            </p>
          </div>
        </div>

        <button
          onClick={() => onCalculateBlastRadius(node.id)}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-rose-600/20 transition"
        >
          Calculate Blast Radius
        </button>
      </div>

      {/* Metrics Row */}
      <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Health Score</span>
          <div className="text-lg font-bold text-emerald-400 mt-1">{node.health_score}%</div>
        </div>
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Monthly Cost</span>
          <div className="text-lg font-bold text-slate-100 mt-1">${node.monthly_cost}</div>
        </div>
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Security Risk Score</span>
          <div className="text-lg font-bold text-amber-400 mt-1">{node.risk_score} / 100</div>
        </div>
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400">Governance Compliance</span>
          <div className="text-lg font-bold text-slate-100 mt-1">{node.governance_status}</div>
        </div>
      </div>

      {/* Upstream & Downstream Lists */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Upstream (Callers) */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
            <ArrowUpRight className="w-4 h-4 text-sky-400" />
            Upstream Callers ({upstreamNodes.length})
          </h3>
          {upstreamNodes.length === 0 ? (
            <p className="text-xs text-slate-500">No upstream callers detected.</p>
          ) : (
            <div className="space-y-2">
              {upstreamNodes.map((u) => (
                <div
                  key={u.id}
                  onClick={() => onSelectNode(u)}
                  className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700 transition"
                >
                  <span className="text-xs font-semibold text-slate-200">{u.name}</span>
                  <span className="text-[11px] text-slate-400">{u.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Downstream (Dependencies) */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
            <ArrowDownRight className="w-4 h-4 text-indigo-400" />
            Downstream Dependencies ({downstreamNodes.length})
          </h3>
          {downstreamNodes.length === 0 ? (
            <p className="text-xs text-slate-500">No downstream dependencies detected.</p>
          ) : (
            <div className="space-y-2">
              {downstreamNodes.map((d) => (
                <div
                  key={d.id}
                  onClick={() => onSelectNode(d)}
                  className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700 transition"
                >
                  <span className="text-xs font-semibold text-slate-200">{d.name}</span>
                  <span className="text-[11px] text-slate-400">{d.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
