import React from 'react';
import { ServiceReliabilityProfile } from '../../types/reliability';
import { Activity, ShieldCheck } from 'lucide-react';

interface SloComplianceChartProps {
  services: ServiceReliabilityProfile[];
}

export const SloComplianceChart: React.FC<SloComplianceChartProps> = ({ services }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">SLO Compliance Visualizer (Target vs Actual)</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Service Availability Compliance</span>
      </div>

      <div className="space-y-3">
        {services.map((s) => {
          const target = s.slo_target;
          const actual = s.availability_pct;
          const pctWidth = Math.max(10, Math.min(100, (actual / 100.0) * 100.0));
          const isBreached = actual < target;

          return (
            <div key={s.service_id} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-white">{s.service_name}</span>
                <span className="font-mono text-slate-300">
                  Actual: <strong className={isBreached ? 'text-rose-400' : 'text-emerald-400'}>{actual}%</strong> | Target: {target}%
                </span>
              </div>

              <div className="w-full bg-slate-800 rounded-full h-3 relative overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isBreached ? 'bg-rose-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${pctWidth}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
