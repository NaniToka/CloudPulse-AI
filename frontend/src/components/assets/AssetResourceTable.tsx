import React from 'react';
import {
  Server,
  ShieldAlert,
  ShieldCheck,
  ExternalLink,
  Cpu,
  HardDrive,
  Activity,
  ChevronRight,
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
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.15)]">Healthy</span>;
      case 'warning':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.15)]">Warning</span>;
      case 'critical':
      case 'degraded':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.15)]">Critical</span>;
      case 'stopped':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-800/80 border border-slate-700/80 text-slate-400">Stopped</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-800 text-slate-300">{status}</span>;
    }
  };

  const getProviderBadge = (provider: string) => {
    switch (provider.toUpperCase()) {
      case 'AWS':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">AWS</span>;
      case 'AZURE':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/20">AZURE</span>;
      case 'GCP':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">GCP</span>;
      case 'KUBERNETES':
      case 'K8S':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">K8S</span>;
      default:
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded-md bg-slate-800 text-slate-300">{provider}</span>;
    }
  };

  return (
    <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl overflow-hidden mb-8">
      <div className="p-5 border-b border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Server className="w-5 h-5" />
          </div>
          Cloud Resource Inventory ({resources.length})
        </h2>
        <span className="text-xs font-medium text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-full border border-slate-700/60">
          Click any row for deep-dive resource telemetry & risk details
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300 border-collapse">
          <thead className="bg-slate-950/80 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800/80">
            <tr>
              <th className="py-4 px-5">Resource Identity</th>
              <th className="py-4 px-5">Provider / Region</th>
              <th className="py-4 px-5">Status</th>
              <th className="py-4 px-5">Telemetry Utilization</th>
              <th className="py-4 px-5">Monthly Cost</th>
              <th className="py-4 px-5">Security & Compliance</th>
              <th className="py-4 px-5 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {resources.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400 text-sm">
                  No cloud resources matching current filter criteria.
                </td>
              </tr>
            ) : (
              resources.map((r) => (
                <tr
                  key={r.id}
                  onClick={() => onSelectResource(r)}
                  className="hover:bg-slate-800/60 cursor-pointer transition-colors duration-200 group"
                >
                  {/* Name & Type */}
                  <td className="py-4 px-5">
                    <div className="font-bold text-slate-100 group-hover:text-indigo-400 transition-colors flex items-center gap-2">
                      {r.name}
                      {r.is_orphaned && (
                        <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/30 tracking-wider">
                          ORPHANED
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex items-center gap-2 font-medium">
                      <span className="text-slate-300">{r.service}</span>
                      <span>•</span>
                      <span className="capitalize">{r.resource_type.replace('_', ' ')}</span>
                      <span>•</span>
                      <span className="text-slate-400">Owner: {r.owner}</span>
                    </div>
                  </td>

                  {/* Provider & Region */}
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-2">
                      {getProviderBadge(r.provider)}
                      <span className="text-xs text-slate-200 font-semibold">{r.region}</span>
                    </div>
                    {r.availability_zone && (
                      <div className="text-xs text-slate-400 mt-1 font-mono">{r.availability_zone}</div>
                    )}
                  </td>

                  {/* Status */}
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-2">
                      {getStatusBadge(r.status)}
                    </div>
                  </td>

                  {/* Telemetry */}
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-3 text-xs font-semibold">
                      {r.cpu_percent !== null && (
                        <span className="flex items-center gap-1 text-slate-200 bg-slate-800/80 px-2 py-1 rounded-md border border-slate-700/80">
                          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                          {r.cpu_percent}%
                        </span>
                      )}
                      {r.memory_percent !== null && (
                        <span className="flex items-center gap-1 text-slate-200 bg-slate-800/80 px-2 py-1 rounded-md border border-slate-700/80">
                          <Activity className="w-3.5 h-3.5 text-sky-400" />
                          {r.memory_percent}%
                        </span>
                      )}
                      {r.disk_percent !== null && (
                        <span className="flex items-center gap-1 text-slate-200 bg-slate-800/80 px-2 py-1 rounded-md border border-slate-700/80">
                          <HardDrive className="w-3.5 h-3.5 text-slate-400" />
                          {r.disk_percent}%
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Cost */}
                  <td className="py-4 px-5">
                    <div className="font-extrabold text-slate-100 text-sm">
                      ${r.monthly_cost.toLocaleString()}
                    </div>
                    <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">/ month</div>
                  </td>

                  {/* Security & Governance */}
                  <td className="py-4 px-5">
                    <div className="flex items-center gap-2 text-xs">
                      {r.security_findings_count > 0 ? (
                        <span className="flex items-center gap-1 text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          {r.security_findings_count} findings
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Clean
                        </span>
                      )}
                    </div>
                    <div className="mt-1.5 text-xs font-semibold">
                      {r.governance_compliance_status === 'COMPLIANT' ? (
                        <span className="text-emerald-400">Compliant</span>
                      ) : (
                        <span className="text-rose-400">Non-Compliant</span>
                      )}
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="py-4 px-5 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectResource(r);
                      }}
                      className="p-2 bg-slate-800/90 group-hover:bg-indigo-600 text-slate-300 group-hover:text-white rounded-lg transition-all duration-200 border border-slate-700/80 group-hover:border-indigo-500"
                      title="Inspect Resource Intelligence"
                    >
                      <ChevronRight className="w-4 h-4" />
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
