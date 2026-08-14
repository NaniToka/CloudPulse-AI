import React from 'react';
import { Network, RefreshCw, Play, Search, Filter, ShieldAlert } from 'lucide-react';
import { TopologyOverviewResponse } from '../../types/topology';

interface TopologyHeaderProps {
  overview?: TopologyOverviewResponse | null;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedProvider: string;
  onProviderChange: (p: string) => void;
  selectedRegion: string;
  onRegionChange: (r: string) => void;
  onRefresh: () => void;
  onOpenSimulateModal: () => void;
  isSyncing: boolean;
}

export const TopologyHeader: React.FC<TopologyHeaderProps> = ({
  overview,
  searchQuery,
  onSearchChange,
  selectedProvider,
  onProviderChange,
  selectedRegion,
  onRegionChange,
  onRefresh,
  onOpenSimulateModal,
  isSyncing,
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
                Cloud Topology & Blast-Radius Intelligence
                <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                  Infrastructure Graph
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Unified multi-cloud dependency graph, blast-radius traversal, failure propagation simulation, and single point of failure detection.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onRefresh}
            disabled={isSyncing}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin text-indigo-400' : ''}`} />
            Refresh Graph
          </button>
          <button
            onClick={onOpenSimulateModal}
            className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium rounded-lg shadow-lg shadow-rose-600/20 transition"
          >
            <Play className="w-4 h-4 fill-current" />
            Simulate Failure
          </button>
        </div>
      </div>

      {/* KPI Overview Pills */}
      {overview && (
        <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-center">
            <div className="text-xs text-slate-400">Total Nodes</div>
            <div className="text-xl font-bold text-slate-100 mt-1">{overview.total_nodes}</div>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-center">
            <div className="text-xs text-slate-400">Dependency Edges</div>
            <div className="text-xl font-bold text-slate-100 mt-1">{overview.total_edges}</div>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-center">
            <div className="text-xs text-slate-400">Cloud Providers</div>
            <div className="text-xl font-bold text-indigo-400 mt-1">{overview.total_providers}</div>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-center">
            <div className="text-xs text-slate-400">Unhealthy Nodes</div>
            <div className="text-xl font-bold text-amber-400 mt-1">{overview.unhealthy_nodes_count}</div>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-center">
            <div className="text-xs text-slate-400">SPOFs Detected</div>
            <div className="text-xl font-bold text-rose-400 mt-1">{overview.spof_count}</div>
          </div>
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-center">
            <div className="text-xs text-slate-400">Graph Monthly Cost</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">${overview.total_monthly_cost.toLocaleString()}</div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="mt-5 pt-4 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search topology node or resource..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <select
            value={selectedProvider}
            onChange={(e) => onProviderChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Cloud Providers</option>
            <option value="AWS">AWS</option>
            <option value="Azure">Azure</option>
            <option value="GCP">GCP</option>
            <option value="Kubernetes">Kubernetes</option>
          </select>
        </div>

        <div>
          <select
            value={selectedRegion}
            onChange={(e) => onRegionChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Regions</option>
            <option value="us-east-1">us-east-1</option>
            <option value="eastus">eastus</option>
            <option value="us-central1">us-central1</option>
          </select>
        </div>
      </div>
    </div>
  );
};
