import React from 'react';
import { Server, Activity, ShieldAlert, DollarSign } from 'lucide-react';
import { ServiceHealthMapItem } from '../../types/executive';

interface Props {
  services: ServiceHealthMapItem[];
}

export const ExecutiveServiceHealthMap: React.FC<Props> = ({ services }) => {
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">Executive Service Health Map</h3>
      <p className="text-xs text-slate-400 mb-4">Topology & health overview of core production and staging microservices</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((svc) => (
          <div key={svc.id} className="p-4 bg-slate-950/60 border border-slate-800/70 hover:border-indigo-500/40 rounded-lg transition-all">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-indigo-400" />
                <span className="font-bold text-slate-200 text-sm">{svc.name}</span>
              </div>
              <span className={`px-2 py-0.5 text-xs font-semibold rounded ${
                svc.status === 'HEALTHY' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              }`}>
                {svc.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 pt-2 border-t border-slate-900">
              <div>
                <span className="block text-[10px] text-slate-400 uppercase">Provider / Env</span>
                <span className="font-semibold text-slate-300 uppercase">{svc.provider} / {svc.environment}</span>
              </div>
              <div>
                <span className="block text-[10px] text-slate-400 uppercase">Monthly Cost</span>
                <span className="font-mono font-semibold text-slate-200">{formatCurrency(svc.monthly_cost)}</span>
              </div>
              <div>
                <span className="block text-[10px] text-slate-400 uppercase">Incidents</span>
                <span className={`font-mono font-semibold ${svc.incident_count > 0 ? 'text-rose-400' : 'text-slate-300'}`}>{svc.incident_count} Active</span>
              </div>
              <div>
                <span className="block text-[10px] text-slate-400 uppercase">Dependencies</span>
                <span className="font-mono font-semibold text-slate-300">{svc.dependencies_count} Nodes</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
