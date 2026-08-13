import React from 'react';
import { ReliabilityIncidentItem } from '../../types/reliability';
import { AlertCircle, Link as LinkIcon, ShieldAlert } from 'lucide-react';

interface IncidentCorrelationStreamProps {
  incidents: ReliabilityIncidentItem[];
}

export const IncidentCorrelationStream: React.FC<IncidentCorrelationStreamProps> = ({ incidents }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-rose-400" />
          <h3 className="text-base font-bold text-white">Reliability Events Correlated with Active Incidents</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{incidents.length} Correlated Incidents</span>
      </div>

      <div className="space-y-3">
        {incidents.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-500 bg-slate-800/40 rounded-xl border border-slate-700/50">
            No active reliability incidents correlated with current service profiles.
          </div>
        ) : (
          incidents.map((inc) => (
            <div
              key={inc.incident_id}
              className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-white text-xs">{inc.incident_id}: {inc.title}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                    {inc.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-300">SLO Impact: {inc.slo_impact}</p>
                <div className="text-[11px] text-amber-300 font-mono">
                  Error Budget Impact: {inc.error_budget_impact} | Duration: {inc.duration_minutes}m
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-xs font-mono text-slate-400">{inc.status}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
