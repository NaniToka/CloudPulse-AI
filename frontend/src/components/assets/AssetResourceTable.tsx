import React from 'react';
import {
  Server,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  Cpu,
  HardDrive,
  Activity,
  Layers,
} from 'lucide-react';
import { AssetResourceItem } from '../../types/assets';

interface AssetResourceTableProps {
  resources: AssetResourceItem[];
  onSelectResource: (resource: AssetResourceItem) => void;
}

export const AssetResourceTable: React.FC<AssetResourceTableProps> = ({
  resources,
  onSelectResource,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">Healthy</span>;
      case 'warning':
        return <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400">Warning</span>;
      case 'critical':
      case 'degraded':
        return <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400">Critical</span>;
      case 'stopped':
        return <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-slate-800 border border-slate-700 text-slate-400">Stopped</span>;
      default:
        return <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-slate-800 text-slate-300">{status}</span>;
    }
  };

  const getProviderBadge = (provider: string) => {
    switch (provider.toUpperCase()) {
      case 'AWS':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">AWS</span>;
      case 'AZURE':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">AZURE</span>;
      case 'GCP':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">GCP</span>;
      case 'KUBERNETES':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">K8S</span>;
      default:
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-slate-800 text-slate-300">{provider}</span>;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden mb-6">
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Server className="w-5 h-5 text-indigo-400" />
          Cloud Resource Inventory ({resources.length})
        </h2>
        <span className="text-xs text-slate-400">Click any resource row for deep-dive intelligence</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-3.5 px-4">Resource Identity</th>
              <th className="py-3.5 px-4">Provider / Region</th>
              <th className="py-3.5 px-4">Status & Health</th>
              <th className="py-3.5 px-4">Telemetry Metrics</th>
              <th className="py-3.5 px-4">Monthly Cost</th>
              <th className="py-3.5 px-4">Security / Governance</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {resources.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500 text-sm">
                  No cloud resources matching current filter criteria.
                </td>
              </tr>
            ) : (
              resources.map((r) => (
                <tr
                  key={r.id}
                  onClick={() => onSelectResource(r)}
                  className="hover:bg-slate-800/50 cursor-pointer transition"
                >
                  {/* Name & Type */}
                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-slate-100 flex items-center gap-2">
                      {r.name}
                      {r.is_orphaned && (
                        <span className="px-1.5 py-0.5 text-[10px] font-bold rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                          ORPHANED
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                      <span>{r.service}</span>
                      <span>•</span>
                      <span className="capitalize">{r.resource_type.replace('_', ' ')}</span>
                      <span>•</span>
                      <span>Owner: {r.owner}</span>
                    </div>
                  </td>

                  {/* Provider & Region */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      {getProviderBadge(r.provider)}
                      <span className="text-xs text-slate-300 font-medium">{r.region}</span>
                    </div>
                    {r.availability_zone && (
                      <div className="text-xs text-slate-500 mt-0.5">{r.availability_zone}</div>
                    )}
                  </td>

                  {/* Status */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      {getStatusBadge(r.status)}
                    </div>
                  </td>

                  {/* Telemetry */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-3 text-xs">
                      {r.cpu_percent !== null && (
                        <span className="flex items-center gap-1 text-slate-300">
                          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                          {r.cpu_percent}%
                        </span>
                      )}
                      {r.memory_percent !== null && (
                        <span className="flex items-center gap-1 text-slate-300">
                          <Activity className="w-3.5 h-3.5 text-sky-400" />
                          {r.memory_percent}%
                        </span>
                      )}
                      {r.disk_percent !== null && (
                        <span className="flex items-center gap-1 text-slate-300">
                          <HardDrive className="w-3.5 h-3.5 text-slate-400" />
                          {r.disk_percent}%
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Cost */}
                  <td className="py-3.5 px-4 font-semibold text-slate-100">
                    ${r.monthly_cost.toLocaleString()}
                    <div className="text-[11px] font-normal text-slate-400">/ month</div>
                  </td>

                  {/* Security & Governance */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2 text-xs">
                      {r.security_findings_count > 0 ? (
                        <span className="flex items-center gap-1 text-amber-400 font-medium">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          {r.security_findings_count} findings
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-emerald-400">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Clean
                        </span>
                      )}
                    </div>
                    <div className="mt-1 text-[11px]">
                      {r.governance_compliance_status === 'COMPLIANT' ? (
                        <span className="text-emerald-400">Compliant</span>
                      ) : (
                        <span className="text-rose-400 font-medium">Non-Compliant</span>
                      )}
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectResource(r);
                      }}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
