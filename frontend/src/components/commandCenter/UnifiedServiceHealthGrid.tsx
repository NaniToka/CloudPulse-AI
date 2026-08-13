import React from 'react';
import { Server, Activity, ShieldCheck, Clock, AlertTriangle } from 'lucide-react';

export const UnifiedServiceHealthGrid: React.FC = () => {
  const serviceList = [
    { service: 'api-gateway', health: 'HEALTHY', slo: '99.98%', latency: '38ms', errors: '0.02%', risk: 'LOW' },
    { service: 'auth-service', health: 'HEALTHY', slo: '99.95%', latency: '45ms', errors: '0.04%', risk: 'LOW' },
    { service: 'payment-service', health: 'BREACHED', slo: '98.40%', latency: '780ms', errors: '1.50%', risk: 'HIGH' },
    { service: 'notification-service', health: 'AT_RISK', slo: '99.10%', latency: '120ms', errors: '0.40%', risk: 'MEDIUM' },
    { service: 'analytics-service', health: 'AT_RISK', slo: '99.20%', latency: '210ms', errors: '3.20%', risk: 'MEDIUM' },
    { service: 'frontend', health: 'HEALTHY', slo: '99.99%', latency: '25ms', errors: '0.00%', risk: 'LOW' },
    { service: 'worker-service', health: 'HEALTHY', slo: '99.92%', latency: '85ms', errors: '0.08%', risk: 'LOW' },
  ];

  const getHealthBadge = (health: string) => {
    switch (health) {
      case 'HEALTHY':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'AT_RISK':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'BREACHED':
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Unified Service Health & Performance</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">7 Microservices Monitored</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-4">Health Status</th>
              <th className="py-3 px-4">SLO Compliance</th>
              <th className="py-3 px-4">P95 Latency</th>
              <th className="py-3 px-4">Error Rate</th>
              <th className="py-3 px-4 text-right">Risk Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {serviceList.map((s) => (
              <tr key={s.service} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-4 font-mono font-bold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  {s.service}
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getHealthBadge(s.health)}`}>
                    {s.health}
                  </span>
                </td>
                <td className="py-3 px-4 font-semibold text-white font-mono">{s.slo}</td>
                <td className="py-3 px-4 font-mono text-slate-300">{s.latency}</td>
                <td className="py-3 px-4 font-mono text-slate-300">{s.errors}</td>
                <td className="py-3 px-4 text-right font-mono font-bold text-indigo-300">
                  {s.risk}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
