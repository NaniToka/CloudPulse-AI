import React from 'react';
import { Flame, Clock, AlertTriangle } from 'lucide-react';

interface MultiWindowBurnRateGridProps {
  burnRatesData: any[];
}

export const MultiWindowBurnRateGrid: React.FC<MultiWindowBurnRateGridProps> = ({ burnRatesData }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'ELEVATED':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'NORMAL':
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    }
  };

  const windowOrder = ['5m', '30m', '1h', '6h', '24h', '7d'];

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-rose-400 animate-pulse" />
          <h3 className="text-base font-bold text-white">Multi-Window Burn Rate Intelligence Matrix</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">6 Standard SRE Windows (5m to 7d)</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Service</th>
              {windowOrder.map((w) => (
                <th key={w} className="py-3 px-4 text-center">{w} Window</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {burnRatesData.map((b) => (
              <tr key={b.service} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-mono font-bold text-white">{b.service}</td>
                {windowOrder.map((w) => {
                  const winData = b.multi_window_burn_rates?.[w] || { burn_rate_x: 1.0, severity: 'NORMAL' };
                  return (
                    <td key={w} className="py-3.5 px-4 text-center">
                      <span className={`px-2.5 py-1 rounded text-[10px] font-extrabold border ${getSeverityColor(winData.severity)}`}>
                        {winData.burn_rate_x}x ({winData.severity})
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
