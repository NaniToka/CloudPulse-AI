import React from 'react';
import { Activity, ShieldCheck, Database, Info } from 'lucide-react';

interface DemoTelemetryBannerProps {
  modeIndicator: string;
  totalServices: number;
}

export const DemoTelemetryBanner: React.FC<DemoTelemetryBannerProps> = ({
  modeIndicator,
  totalServices,
}) => {
  return (
    <div className="bg-slate-900/80 border border-indigo-500/30 rounded-xl p-4 shadow-lg backdrop-blur-md relative overflow-hidden">
      <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-500/15 border border-indigo-500/40 rounded-lg text-indigo-400">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-wide">
                ENTERPRISE SLO, SLA & ERROR BUDGET INTELLIGENCE CENTER
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                ACTIVE
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{modeIndicator}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs font-medium">
            <Database className="w-4 h-4 text-indigo-400" />
            <span>Monitored Services: <strong className="text-white">{totalServices}</strong></span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-600/40 text-indigo-300 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>Deterministic Fixtures: LOADED</span>
          </div>
        </div>
      </div>
    </div>
  );
};
