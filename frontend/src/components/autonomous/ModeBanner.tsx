import React from 'react';
import { ShieldCheck, Play, ShieldAlert, Cpu, CheckCircle } from 'lucide-react';

interface ModeBannerProps {
  modeIndicator: string;
  autonomyLevel: number;
  executionMode: string;
}

export const ModeBanner: React.FC<ModeBannerProps> = ({
  modeIndicator,
  autonomyLevel,
  executionMode,
}) => {
  const levelLabels = [
    'Level 0: Observe Only',
    'Level 1: AI Recommend',
    'Level 2: Human Approval Required',
    'Level 3: Auto Low-Risk Remediation',
    'Level 4: Policy-Controlled Autonomous',
  ];

  return (
    <div className="bg-slate-900/80 border border-emerald-500/30 rounded-xl p-4 shadow-lg backdrop-blur-md relative overflow-hidden">
      <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-500/15 border border-emerald-500/40 rounded-lg text-emerald-400">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-wide">
                AUTONOMOUS CLOUD OPERATIONS & SELF-HEALING CENTER
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                ACTIVE
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{modeIndicator}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs font-medium">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Mode: <strong className="text-emerald-400">{executionMode}</strong></span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs font-medium">
            <CheckCircle className="w-4 h-4 text-blue-400" />
            <span>{levelLabels[autonomyLevel] || `Level ${autonomyLevel}`}</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-600/40 text-emerald-300 text-xs font-semibold">
            <ShieldAlert className="w-4 h-4" />
            <span>Safety Guardrails: ENABLED</span>
          </div>
        </div>
      </div>
    </div>
  );
};
