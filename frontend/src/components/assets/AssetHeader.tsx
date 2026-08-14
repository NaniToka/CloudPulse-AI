import React from 'react';
import { RefreshCw, Search, Database, Cpu, Layers } from 'lucide-react';

interface AssetHeaderProps {
  modeIndicator?: string;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedProvider: string;
  onProviderChange: (p: string) => void;
  selectedType: string;
  onTypeChange: (t: string) => void;
  onRefresh: () => void;
  onDiscover: () => void;
  isSyncing: boolean;
}

export const AssetHeader: React.FC<AssetHeaderProps> = ({
  modeIndicator = 'Demo / Local Asset Data',
  searchQuery,
  onSearchChange,
  selectedProvider,
  onProviderChange,
  selectedType,
  onTypeChange,
  onRefresh,
  onDiscover,
  isSyncing,
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl mb-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
                Cloud Asset Intelligence & Resource Inventory
                <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                  {modeIndicator}
                </span>
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Unified multi-cloud resource graph integrated with FinOps costs, Security findings, Governance compliance, and Topology relationships.
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
            Refresh Telemetry
          </button>
          <button
            onClick={onDiscover}
            disabled={isSyncing}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg shadow-lg shadow-indigo-600/20 transition disabled:opacity-50"
          >
            <Cpu className="w-4 h-4" />
            Trigger Asset Discovery
          </button>
        </div>
      </div>

      <div className="mt-6 pt-5 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search resource name or service..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Provider Select */}
        <div>
          <select
            value={selectedProvider}
            onChange={(e) => onProviderChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Cloud Providers</option>
            <option value="AWS">AWS (Amazon Web Services)</option>
            <option value="Azure">Azure (Microsoft Azure)</option>
            <option value="GCP">GCP (Google Cloud Platform)</option>
            <option value="Kubernetes">Kubernetes</option>
          </select>
        </div>

        {/* Resource Type Select */}
        <div>
          <select
            value={selectedType}
            onChange={(e) => onTypeChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Resource Types</option>
            <option value="virtual_machine">Virtual Machines / Instances</option>
            <option value="database">Database Engines</option>
            <option value="storage">Storage & Storage Buckets</option>
            <option value="kubernetes_cluster">Kubernetes Clusters</option>
            <option value="pod">Kubernetes Workload Pods</option>
          </select>
        </div>

        {/* Info summary badge */}
        <div className="flex items-center justify-end px-3 py-2 bg-slate-950/60 rounded-lg border border-slate-800 text-xs text-slate-400">
          <Database className="w-3.5 h-3.5 mr-1.5 text-indigo-400" />
          <span>Real-time Asset Graph Sync</span>
        </div>
      </div>
    </div>
  );
};
