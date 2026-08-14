import React from 'react';
import { GitCommit, ArrowRight, Layers } from 'lucide-react';
import { AssetTopologyResponse } from '../../types/assets';

interface AssetTopologyGraphProps {
  topology?: AssetTopologyResponse | null;
}

export const AssetTopologyGraph: React.FC<AssetTopologyGraphProps> = ({ topology }) => {
  if (!topology) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <GitCommit className="w-5 h-5 text-indigo-400" />
          Multi-Cloud Resource Dependency Topology
        </h2>
        <span className="text-xs text-slate-400">
          {topology.nodes.length} Nodes • {topology.edges.length} Dependency Edges
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-5">
        Visual representation of resource dependency relationships connecting Kubernetes workloads, virtual machine instances, databases, and storage buckets.
      </p>

      {/* Interactive Topology Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {topology.edges.map((edge, idx) => {
          const srcNode = topology.nodes.find((n) => n.id === edge.source);
          const tgtNode = topology.nodes.find((n) => n.id === edge.target);

          if (!srcNode || !tgtNode) return null;

          return (
            <div
              key={idx}
              className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {edge.label}
                </span>
                <span className="text-xs text-slate-500">{srcNode.provider} → {tgtNode.provider}</span>
              </div>

              <div className="flex items-center justify-between gap-2 my-2">
                <div className="flex-1 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                  <div className="font-semibold text-xs text-slate-200 truncate">{srcNode.name}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{srcNode.type}</div>
                </div>

                <ArrowRight className="w-4 h-4 text-indigo-400 shrink-0" />

                <div className="flex-1 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                  <div className="font-semibold text-xs text-slate-200 truncate">{tgtNode.name}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{tgtNode.type}</div>
                </div>
              </div>

              <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>Source Cost: ${srcNode.cost}/mo</span>
                <span>Target Cost: ${tgtNode.cost}/mo</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
