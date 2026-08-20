import React from 'react';
import { Server, Activity, ShieldAlert, DollarSign, Layers } from 'lucide-react';
import { ServiceHealthMapItem } from '../../types/executive';

interface Props {
  services: ServiceHealthMapItem[];
}

export const ExecutiveServiceHealthMap: React.FC<Props> = ({ services }) => {
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="p-6 bg-slate-900/70 border border-slate-800/80 rounded-2xl backdrop-blur-xl shadow-2xl relative overflow-hidden">
      {/* Top Accent Line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-sky-500" />

      <div className="flex items-center justify-between mb-1">
        <h3 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Server className="w-4 h-4" />
          </div>
          Executive Service Health Map
        </h3>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700/80">
          {services.length} Microservices
        </span>
      </div>
      <p className="text-xs text-slate-400 mb-4">Topology & health overview of core production and staging workloads</p>

      {/* Clean 2-column grid so cards have wide horizontal breathing room */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {services.map((svc) => (
          <div
            key={svc.id}
            className="p-4 bg-slate-950/80 hover:bg-slate-950 border border-slate-800/80 hover:border-indigo-500/40 rounded-xl transition-all duration-200 relative overflow-hidden group shadow-lg"
          >
            {/* Header: Service Name & Status Badge */}
            <div className="flex items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <Server className="w-4 h-4 text-indigo-400 shrink-0 group-hover:scale-110 transition-transform" />
                <span className="font-bold text-slate-100 text-sm truncate" title={svc.name}>
                  {svc.name}
                </span>
              </div>
              <span
                className={`px-2.5 py-0.5 text-xs font-bold rounded-full shrink-0 border ${
                  svc.status === 'HEALTHY'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_8px_rgba(16,185,129,0.15)]'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/30 shadow-[0_0_8px_rgba(244,63,94,0.15)]'
                }`}
              >
                {svc.status}
              </span>
            </div>

            {/* Metrics 2x2 Grid with min-w-0 and clean alignment */}
            <div className="grid grid-cols-2 gap-3 text-xs pt-2.5 border-t border-slate-800/80">
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Provider / Env</span>
                <span className="font-bold text-slate-200 text-[11px] truncate block mt-0.5" title={`${svc.provider} / ${svc.environment}`}>
                  {svc.provider} • <span className="text-slate-400 font-medium uppercase text-[10px]">{svc.environment}</span>
                </span>
              </div>
              <div className="min-w-0 text-right">
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Monthly Cost</span>
                <span className="font-mono font-extrabold text-slate-100 text-[11px] mt-0.5 block">{formatCurrency(svc.monthly_cost)}</span>
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active Incidents</span>
                <span className={`font-mono font-bold text-[11px] mt-0.5 block ${svc.incident_count > 0 ? 'text-rose-400' : 'text-slate-300'}`}>
                  {svc.incident_count} Active
                </span>
              </div>
              <div className="min-w-0 text-right">
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Dependencies</span>
                <span className="font-mono font-bold text-slate-300 text-[11px] mt-0.5 block">{svc.dependencies_count} Nodes</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
