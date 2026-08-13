import React from 'react';
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Lock,
  Play,
  RotateCcw,
  ShieldCheck,
  Zap,
} from 'lucide-react';

interface RemediationPipelineFlowProps {
  activeStep?: number;
}

export const RemediationPipelineFlow: React.FC<RemediationPipelineFlowProps> = ({
  activeStep = 3,
}) => {
  const steps = [
    { title: 'EVENT DETECTED', desc: 'Incident Signal', icon: Activity },
    { title: 'CORRELATION & RCA', desc: 'Root Cause AI', icon: Zap },
    { title: 'REMEDIATION PLAN', desc: 'Action Selection', icon: Play },
    { title: 'RISK & PRECONDITIONS', desc: 'Locks & Rules', icon: Lock },
    { title: 'APPROVAL & POLICY', desc: 'RBAC Check', icon: ShieldCheck },
    { title: 'EXECUTION', desc: 'Provider Adapter', icon: Play },
    { title: 'POST-VERIFICATION', desc: 'Health Check', icon: CheckCircle2 },
    { title: 'SUCCESS / ROLLBACK', desc: 'Audit Logged', icon: RotateCcw },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Autonomous Remediation Lifecycle Pipeline</h3>
          <p className="text-xs text-slate-400">
            Deterministic state machine from signal detection to post-action state verification or rollback.
          </p>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Pipeline Mode: <strong className="text-emerald-400">DRY_RUN / SIMULATED</strong>
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isDone = idx < activeStep;
          const isCurrent = idx === activeStep;

          return (
            <div
              key={step.title}
              className={`p-3 rounded-lg border flex flex-col justify-between transition-all ${
                isCurrent
                  ? 'border-emerald-500 bg-emerald-950/40 text-emerald-300 ring-1 ring-emerald-500/40 shadow-lg shadow-emerald-950/30'
                  : isDone
                  ? 'border-slate-700 bg-slate-800/80 text-slate-300'
                  : 'border-slate-800/80 bg-slate-900/40 text-slate-500'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    isCurrent
                      ? 'bg-emerald-500 text-slate-950 animate-pulse'
                      : isDone
                      ? 'bg-slate-700 text-slate-300'
                      : 'bg-slate-800 text-slate-500'
                  }`}
                >
                  Step {idx + 1}
                </span>
                <Icon className={`w-4 h-4 ${isCurrent ? 'text-emerald-400' : isDone ? 'text-blue-400' : 'text-slate-600'}`} />
              </div>
              <div className="font-bold text-[11px] leading-tight mb-1 text-white">{step.title}</div>
              <div className="text-[10px] text-slate-400">{step.desc}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
