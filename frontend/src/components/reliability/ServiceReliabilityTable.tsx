import React from 'react';
import { ServiceReliabilityProfile } from '../../types/reliability';
import { Server, Activity, ShieldCheck, Flame, ArrowRight } from 'lucide-react';

interface ServiceReliabilityTableProps {
  services: ServiceReliabilityProfile[];
  onSelectService: (service: ServiceReliabilityProfile) => void;
}

export const ServiceReliabilityTable: React.FC<ServiceReliabilityTableProps> = ({
  services,
  onSelectService,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'HEALTHY':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'AT_RISK':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'BREACHING':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      case 'BREACHED':
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white">Service Reliability Profiles</h3>
          <p className="text-xs text-slate-400">Click any service to inspect full SRE telemetry detail, error budget & dependencies.</p>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{services.length} Monitored Services</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-4">Provider</th>
              <th className="py-3 px-4">Availability</th>
              <th className="py-3 px-4">P95 / P99 Latency</th>
              <th className="py-3 px-4">Error Rate</th>
              <th className="py-3 px-4">SLO Target</th>
              <th className="py-3 px-4">Error Budget</th>
              <th className="py-3 px-4">Burn Rate</th>
              <th className="py-3 px-4">Risk Score</th>
              <th className="py-3 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {services.length === 0 ? (
              <tr>
                <td colSpan={10} className="py-8 text-center text-slate-500">
                  No services matching current filter criteria.
                </td>
              </tr>
            ) : (
              services.map((svc) => (
                <tr
                  key={svc.service_id}
                  onClick={() => onSelectService(svc)}
                  className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                >
                  <td className="py-3.5 px-4 font-mono font-bold text-white flex items-center gap-2">
                    <Server className="w-4 h-4 text-indigo-400 shrink-0" />
                    {svc.service_name}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">{svc.provider} ({svc.region})</td>
                  <td className="py-3.5 px-4 font-mono font-bold text-emerald-300">{svc.availability_pct}%</td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">
                    {svc.latency_p95_ms}ms <span className="text-slate-500">/ {svc.latency_p99_ms}ms</span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">{svc.error_rate_pct}%</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">{svc.slo_target}%</td>
                  <td className="py-3.5 px-4 font-mono font-bold text-indigo-300">
                    {svc.error_budget_remaining_pct}% remaining
                  </td>
                  <td className="py-3.5 px-4 font-mono font-bold text-amber-400">{svc.burn_rate}x</td>
                  <td className="py-3.5 px-4 font-mono font-extrabold text-white">{svc.risk_score} pts</td>
                  <td className="py-3.5 px-4 text-right">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold border ${getStatusBadge(svc.status)}`}>
                      {svc.status}
                    </span>
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
