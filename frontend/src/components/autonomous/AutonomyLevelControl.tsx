import React from 'react';
import { Eye, Lightbulb, UserCheck, Zap, ShieldCheck } from 'lucide-react';

interface AutonomyLevelControlProps {
  currentLevel: number;
  onLevelChange: (level: number) => void;
}

export const AutonomyLevelControl: React.FC<AutonomyLevelControlProps> = ({
  currentLevel,
  onLevelChange,
}) => {
  const levels = [
    {
      level: 0,
      title: 'Level 0: Observe',
      desc: 'System detects incidents and issues recommendations only. No actions executed.',
      icon: Eye,
      color: 'border-slate-700 text-slate-400 bg-slate-900/60',
      activeColor: 'border-slate-500 text-slate-200 bg-slate-800/90 shadow-slate-500/20',
    },
    {
      level: 1,
      title: 'Level 1: Recommend',
      desc: 'AI generates detailed remediation plans. Human must approve all plans.',
      icon: Lightbulb,
      color: 'border-blue-900/50 text-blue-400 bg-slate-900/60',
      activeColor: 'border-blue-500 text-blue-300 bg-blue-950/40 shadow-blue-500/20',
    },
    {
      level: 2,
      title: 'Level 2: Require Approval',
      desc: 'Automated validation & policy check. Pre-approved low risk require human confirmation.',
      icon: UserCheck,
      color: 'border-indigo-900/50 text-indigo-400 bg-slate-900/60',
      activeColor: 'border-indigo-500 text-indigo-300 bg-indigo-950/40 shadow-indigo-500/20',
    },
    {
      level: 3,
      title: 'Level 3: Auto Low-Risk',
      desc: 'LOW-risk actions (restart, clear cache) execute automatically. MEDIUM+ require approval.',
      icon: Zap,
      color: 'border-amber-900/50 text-amber-400 bg-slate-900/60',
      activeColor: 'border-amber-500 text-amber-300 bg-amber-950/40 shadow-amber-500/20',
    },
    {
      level: 4,
      title: 'Level 4: Policy Controlled',
      desc: 'Fully autonomous self-healing within strict policy thresholds & verification guardrails.',
      icon: ShieldCheck,
      color: 'border-emerald-900/50 text-emerald-400 bg-slate-900/60',
      activeColor: 'border-emerald-500 text-emerald-300 bg-emerald-950/40 shadow-emerald-500/20',
    },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">System Autonomy Level (0 - 4)</h3>
          <p className="text-xs text-slate-400">
            Configure the balance between automated cloud self-healing and human oversight.
          </p>
        </div>
        <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-full text-xs font-bold">
          Active Level: {currentLevel}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {levels.map((item) => {
          const Icon = item.icon;
          const isActive = currentLevel === item.level;
          return (
            <button
              key={item.level}
              onClick={() => onLevelChange(item.level)}
              className={`flex flex-col text-left p-3.5 rounded-lg border transition-all duration-200 ${
                isActive ? `${item.activeColor} ring-2 ring-emerald-500/50 shadow-md` : `${item.color} hover:border-slate-600`
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className="w-5 h-5" />
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    isActive ? 'bg-emerald-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  L{item.level}
                </span>
              </div>
              <div className="font-semibold text-xs text-white mb-1">{item.title}</div>
              <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-3">{item.desc}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
