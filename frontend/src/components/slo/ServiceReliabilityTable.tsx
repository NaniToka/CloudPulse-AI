import React, { useState } from 'react';
import { ServiceReliability } from '../../types/slo';
import { ShieldCheck, AlertTriangle, AlertCircle, Search, ArrowUpDown } from 'lucide-react';

interface ServiceReliabilityTableProps {
  services: ServiceReliability[];
  onSelectService: (service: string) => void;
}

export const ServiceReliabilityTable: React.FC<ServiceReliabilityTableProps> = ({
  services,
  onSelectService,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredServices = services.filter((svc) => {
    const matchesSearch = svc.service.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' ? true : svc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'HEALTHY':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'AT_RISK':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'BREACHED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Service Reliability Matrix</h3>
          <p className="text-xs text-slate-400">
            Real-time availability, latency, error rate, and calculated reliability scores per microservice.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-48">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search service..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-800/80 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800/80 border border-slate-700 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="HEALTHY">HEALTHY</option>
            <option value="AT_RISK">AT_RISK</option>
            <option value="BREACHED">BREACHED</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-4">Availability</th>
              <th className="py-3 px-4">P95 Latency</th>
              <th className="py-3 px-4">Error Rate</th>
              <th className="py-3 px-4">Target SLO</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Reliability Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredServices.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No services match current filter criteria.
                </td>
              </tr>
            ) : (
              filteredServices.map((svc) => (
                <tr
                  key={svc.service}
                  onClick={() => onSelectService(svc.service)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-4 font-mono font-bold text-white flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                    {svc.service}
                  </td>
                  <td className="py-3 px-4 font-semibold text-white">
                    {svc.availability_pct}%
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {svc.latency_p95_ms} ms
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {svc.error_rate_pct}%
                  </td>
                  <td className="py-3 px-4 text-slate-400 font-semibold">
                    {svc.target_slo}%
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getStatusBadge(
                        svc.status
                      )}`}
                    >
                      {svc.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className="font-mono font-bold text-sm text-emerald-400">
                      {svc.reliability_score}
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
