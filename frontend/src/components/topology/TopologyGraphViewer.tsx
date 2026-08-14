import React, { useState } from 'react';
import { Network, ZoomIn, ZoomOut, RotateCcw, Activity, ShieldAlert, Layers } from 'lucide-react';
import { TopologyEdgeItem, TopologyNodeItem } from '../../types/topology';

interface TopologyGraphViewerProps {
  nodes: TopologyNodeItem[];
  edges: TopologyEdgeItem[];
  selectedNodeId?: string | null;
  onSelectNode: (node: TopologyNodeItem) => void;
}

export const TopologyGraphViewer: React.FC<TopologyGraphViewerProps> = ({
  nodes,
  edges,
  selectedNodeId,
  onSelectNode,
}) => {
  const [zoom, setZoom] = useState(1);

  const getProviderBadge = (provider: string) => {
    switch (provider.toUpperCase()) {
      case 'AWS':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'AZURE':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
      case 'GCP':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      default:
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    }
  };

  const getStatusBorder = (status: string) => {
    switch (status.toUpperCase()) {
      case 'HEALTHY':
        return 'border-emerald-500/40 bg-slate-900/90';
      case 'DEGRADED':
        return 'border-amber-500/60 bg-amber-950/20';
      case 'CRITICAL':
        return 'border-rose-500/80 bg-rose-950/30';
      default:
        return 'border-slate-800 bg-slate-900';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6 relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Network className="w-5 h-5 text-indigo-400" />
          Interactive Multi-Cloud Topology Canvas
        </h2>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom((z) => Math.min(1.5, z + 0.1))}
            className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-300 transition"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(0.7, z - 0.1))}
            className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-300 transition"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-300 transition"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Topology Canvas Viewport */}
      <div
        className="min-h-[420px] bg-slate-950 rounded-xl border border-slate-800 p-6 flex flex-col justify-between transition-transform duration-200"
        style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }}
      >
        {nodes.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
            No topology nodes available for current filter criteria.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {nodes.map((node) => {
              const isSelected = selectedNodeId === node.id;
              const statusStyle = getStatusBorder(node.status);
              const provStyle = getProviderBadge(node.provider);

              return (
                <div
                  key={node.id}
                  onClick={() => onSelectNode(node)}
                  className={`p-4 rounded-xl border ${statusStyle} ${
                    isSelected ? 'ring-2 ring-indigo-500 shadow-indigo-500/20' : ''
                  } cursor-pointer hover:border-indigo-500/60 transition shadow-lg`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${provStyle}`}>
                      {node.provider}
                    </span>
                    <span className="text-xs text-slate-400 capitalize">{node.type}</span>
                  </div>

                  <div className="mt-3 font-bold text-sm text-slate-100 truncate">{node.name}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{node.region}</div>

                  <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                    <span
                      className={`font-semibold ${
                        node.status === 'HEALTHY'
                          ? 'text-emerald-400'
                          : node.status === 'DEGRADED'
                          ? 'text-amber-400'
                          : 'text-rose-400'
                      }`}
                    >
                      {node.status}
                    </span>
                    <span className="text-slate-300 font-medium">${node.monthly_cost}/mo</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Legend */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-4">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Healthy</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Degraded</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Critical</span>
          </div>

          <div>
            <span>Click any node to view upstream / downstream dependencies & blast radius.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
