import React from 'react';
import { DependencyImpactItem } from '../../types/reliability';
import { GitCommit, ArrowRight, Network } from 'lucide-react';

interface DependencyImpactVisualizerProps {
  dependencies: DependencyImpactItem[];
}

export const DependencyImpactVisualizer: React.FC<DependencyImpactVisualizerProps> = ({ dependencies }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Dependency Reliability & Cascade Impact</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Service Dependency Intelligence</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dependencies.map((d, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white text-sm">{d.service_name}</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                  d.dependency_health === 'HEALTHY'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}
              >
                {d.dependency_health}
              </span>
            </div>

            <div className="text-xs text-slate-300 space-y-1.5 font-mono">
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Upstream:</span>
                <span className="text-indigo-300">
                  {d.upstream_dependencies.length > 0 ? d.upstream_dependencies.join(', ') : 'None (Entrypoint)'}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Downstream:</span>
                <span className="text-indigo-300">
                  {d.downstream_dependencies.length > 0 ? d.downstream_dependencies.join(', ') : 'None (Leaf)'}
                </span>
              </div>
            </div>

            <p className="text-xs text-amber-200 border-t border-slate-700/50 pt-2">{d.dependency_correlation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
