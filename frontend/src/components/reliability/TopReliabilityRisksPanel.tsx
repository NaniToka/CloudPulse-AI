import React from 'react';
import { ReliabilityRiskItem } from '../../types/reliability';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

interface TopReliabilityRisksPanelProps {
  risks: ReliabilityRiskItem[];
}

export const TopReliabilityRisksPanel: React.FC<TopReliabilityRisksPanelProps> = ({ risks }) => {
  const getSeverityBadge = (level: string) => {
    switch (level.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-bold text-white">Top Service Reliability Risks</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Deterministic Risk Analysis</span>
      </div>

      <div className="space-y-3">
        {risks.map((r) => (
          <div key={r.service_name} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-white text-sm">{r.service_name}</span>
                <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold border ${getSeverityBadge(r.risk_level)}`}>
                  {r.risk_level} ({r.risk_score} pts)
                </span>
              </div>
            </div>

            <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
              {r.top_factors.map((factor, idx) => (
                <li key={idx} className="text-amber-200">{factor}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};
