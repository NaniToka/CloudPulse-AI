import React from 'react';
import { GitCommit, ArrowRight, Layers, DollarSign, Server, Database, Box, HardDrive, Cpu } from 'lucide-react';
import { AssetTopologyResponse, AssetNode } from '../../types/assets';

interface AssetTopologyGraphProps {
  topology?: AssetTopologyResponse | null;
}

const getRelationBadgeStyle = (label: string) => {
  switch (label.toUpperCase()) {
    case 'CONNECTS_TO':
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.15)]';
    case 'WRITES_TO':
      return 'bg-purple-500/10 text-purple-400 border-purple-500/30 shadow-[0_0_10px_rgba(168,85,247,0.15)]';
    case 'DEPLOYS_ON':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.15)]';
    case 'QUERIES':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.15)]';
    case 'CONTAINED_IN':
      return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 shadow-[0_0_10px_rgba(99,102,241,0.15)]';
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700';
  }
};

const getProviderBadgeStyle = (provider: string) => {
  switch (provider.toLowerCase()) {
    case 'aws':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'gcp':
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
    case 'azure':
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    case 'kubernetes':
    case 'k8s':
      return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    default:
      return 'bg-slate-800 text-slate-400 border-slate-700';
  }
};

const getNodeIcon = (type: string) => {
  const t = type.toLowerCase();
  if (t.includes('database') || t.includes('rds') || t.includes('postgres') || t.includes('bigquery')) {
    return <Database className="w-3.5 h-3.5 text-purple-400 shrink-0" />;
  }
  if (t.includes('storage') || t.includes('s3') || t.includes('bucket')) {
    return <HardDrive className="w-3.5 h-3.5 text-cyan-400 shrink-0" />;
  }
  if (t.includes('pod') || t.includes('container') || t.includes('k8s')) {
    return <Box className="w-3.5 h-3.5 text-indigo-400 shrink-0" />;
  }
  if (t.includes('vm') || t.includes('ec2') || t.includes('virtual_machine') || t.includes('compute')) {
    return <Cpu className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
  }
  return <Server className="w-3.5 h-3.5 text-slate-400 shrink-0" />;
};

export const AssetTopologyGraph: React.FC<AssetTopologyGraphProps> = ({ topology }) => {
  if (!topology || !topology.nodes || topology.nodes.length === 0) return null;

  return (
    <div className="relative overflow-hidden bg-slate-900/70 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-2xl mb-8">
      {/* Top ambient gradient accent bar */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <GitCommit className="w-5 h-5" />
            </div>
            Multi-Cloud Resource Dependency Topology
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Visual topology mapping cross-cloud dependency vectors connecting Kubernetes workloads, VMs, databases, and storage.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800/90 text-slate-300 border border-slate-700/80 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            {topology.nodes.length} Nodes
          </span>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800/90 text-slate-300 border border-slate-700/80">
            {topology.edges.length} Dependency Hops
          </span>
        </div>
      </div>

      {/* Interactive Topology Cards Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-5 mt-5">
        {topology.edges.map((edge, idx) => {
          const srcNode = topology.nodes.find((n) => n.id === edge.source);
          const tgtNode = topology.nodes.find((n) => n.id === edge.target);

          if (!srcNode || !tgtNode) return null;

          return (
            <div
              key={idx}
              className="group relative p-4 bg-slate-950/80 hover:bg-slate-900/90 border border-slate-800/80 hover:border-indigo-500/40 rounded-xl transition-all duration-300 shadow-lg hover:shadow-indigo-500/10 flex flex-col justify-between"
            >
              {/* Relation header */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getRelationBadgeStyle(edge.label)}`}>
                  {edge.label}
                </span>
                <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
                  <span className={`px-1.5 py-0.5 rounded border uppercase text-[10px] font-semibold ${getProviderBadgeStyle(srcNode.provider)}`}>
                    {srcNode.provider}
                  </span>
                  <span>→</span>
                  <span className={`px-1.5 py-0.5 rounded border uppercase text-[10px] font-semibold ${getProviderBadgeStyle(tgtNode.provider)}`}>
                    {tgtNode.provider}
                  </span>
                </div>
              </div>

              {/* Source & Target Nodes Flow */}
              <div className="flex items-center justify-between gap-2 my-1">
                {/* Source Node Box */}
                <div
                  className="flex-1 min-w-0 bg-slate-900/90 group-hover:bg-slate-950/90 p-3 rounded-lg border border-slate-800/90 group-hover:border-slate-700/80 transition-colors"
                  title={`${srcNode.name} (${srcNode.type})`}
                >
                  <div className="flex items-center gap-1.5 mb-1">
                    {getNodeIcon(srcNode.type)}
                    <span className="font-semibold text-xs text-slate-200 truncate">{srcNode.name}</span>
                  </div>
                  <div className="text-[10px] uppercase tracking-wider font-medium text-slate-500 truncate">
                    {srcNode.type.replace('_', ' ')}
                  </div>
                </div>

                {/* Flow Arrow */}
                <div className="p-1.5 rounded-full bg-slate-900 border border-slate-800 group-hover:border-indigo-500/30 text-indigo-400 shrink-0 transition-transform group-hover:scale-110">
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </div>

                {/* Target Node Box */}
                <div
                  className="flex-1 min-w-0 bg-slate-900/90 group-hover:bg-slate-950/90 p-3 rounded-lg border border-slate-800/90 group-hover:border-slate-700/80 transition-colors"
                  title={`${tgtNode.name} (${tgtNode.type})`}
                >
                  <div className="flex items-center gap-1.5 mb-1">
                    {getNodeIcon(tgtNode.type)}
                    <span className="font-semibold text-xs text-slate-200 truncate">{tgtNode.name}</span>
                  </div>
                  <div className="text-[10px] uppercase tracking-wider font-medium text-slate-500 truncate">
                    {tgtNode.type.replace('_', ' ')}
                  </div>
                </div>
              </div>

              {/* Bottom Cost Breakdown */}
              <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-medium text-slate-400">
                <span className="flex items-center gap-1">
                  <DollarSign className="w-3 h-3 text-emerald-400" />
                  Source: <strong className="text-slate-200">${srcNode.cost.toLocaleString()}/mo</strong>
                </span>
                <span className="flex items-center gap-1">
                  <DollarSign className="w-3 h-3 text-emerald-400" />
                  Target: <strong className="text-slate-200">${tgtNode.cost.toLocaleString()}/mo</strong>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
