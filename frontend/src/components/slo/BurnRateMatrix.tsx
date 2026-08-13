import React from 'react';
import { BurnRate } from '../../types/slo';
import { Flame, AlertTriangle, ShieldCheck, AlertCircle } from 'lucide-react';

interface BurnRateMatrixProps {
  burnRates: BurnRate[];
}

export const BurnRateMatrix: React.FC<BurnRateMatrixProps> = ({ burnRates }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'border-rose-500/40 bg-rose-950/30 text-rose-300';
      case 'HIGH':
        return 'border-amber-500/40 bg-amber-950/30 text-amber-300';
      case 'ELEVATED':
        return 'border-indigo-500/40 bg-indigo-950/30 text-indigo-300';
      case 'NORMAL':
      default:
        return 'border-emerald-500/40 bg-emerald-950/30 text-emerald-300';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-amber-400 animate-pulse" />
          <h3 className="text-base font-semibold text-white">Multi-Window Burn Rate Intelligence</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">4 Window Detection (1h, 6h, 24h, 7d)</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {burnRates.map((br) => {
          const colorClass = getSeverityColor(br.severity);

          return (
            <div key={br.service} className={`p-4 rounded-xl border ${colorClass} space-y-2 flex flex-col justify-between`}>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-white text-xs">{br.service}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-slate-900/80">
                    {br.severity}
                  </span>
                </div>
                <div className="text-2xl font-extrabold font-mono mb-1">
                  {br.burn_rate_x}x <span className="text-xs font-normal font-sans text-slate-400">burn rate</span>
                </div>
                <p className="text-[11px] text-slate-300 leading-relaxed">{br.explanation}</p>
              </div>

              <div className="text-[10px] text-slate-400 border-t border-slate-700/50 pt-2 mt-2 flex justify-between">
                <span>Observed: {(br.observed_failure_rate * 100).toFixed(2)}%</span>
                <span>Allowed: {(br.allowed_failure_rate * 100).toFixed(2)}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
