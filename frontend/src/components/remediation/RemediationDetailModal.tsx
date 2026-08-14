import React from 'react';
import { RemediationPlan } from '../../types/remediation';
import { X, Server, Activity, ShieldCheck, Zap, RotateCcw, AlertTriangle, ArrowLeftRight } from 'lucide-react';

interface RemediationDetailModalProps {
  plan: RemediationPlan | null;
  onClose: () => void;
  onExecute?: (planId: string) => Promise<void>;
  onDryRun?: (planId: string) => Promise<void>;
}

export const RemediationDetailModal: React.FC<RemediationDetailModalProps> = ({
  plan,
  onClose,
  onExecute,
  onDryRun,
}) => {
  if (!plan) return null;

  const getRiskBadge = (risk: string) => {
    switch (risk.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl space-y-6 p-6 relative">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-500/15 border border-indigo-500/30 rounded-xl text-indigo-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-extrabold text-white font-mono">{plan.action_type}</h2>
                <span className={`px-2.5 py-0.5 rounded text-xs font-extrabold border ${getRiskBadge(plan.risk_level)}`}>
                  {plan.risk_level} RISK
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Affected Resource: <strong className="text-white font-mono">{plan.affected_resource}</strong> ({plan.provider} - {plan.environment})</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Key Overview Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-[10px] uppercase font-bold">Status</div>
              <div className="text-base font-bold font-mono text-emerald-400 mt-1">{plan.status}</div>
              <div className="text-[10px] text-slate-500">Lifecycle State</div>
            </div>

            <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-[10px] uppercase font-bold">Execution Mode</div>
              <div className="text-base font-bold font-mono text-amber-400 mt-1">{plan.execution_mode}</div>
              <div className="text-[10px] text-slate-500">Local Simulation</div>
            </div>

            <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-[10px] uppercase font-bold">Confidence Score</div>
              <div className="text-base font-bold font-mono text-indigo-300 mt-1">{Math.round(plan.confidence_score * 100)}%</div>
              <div className="text-[10px] text-slate-500">Deterministic Model</div>
            </div>

            <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-[10px] uppercase font-bold">Rollback Support</div>
              <div className="text-base font-bold font-mono text-blue-400 mt-1">
                {plan.rollback_supported ? 'AVAILABLE' : 'NOT_SUPPORTED'}
              </div>
              <div className="text-[10px] text-slate-500">State Diffs Tracked</div>
            </div>
          </div>

          {/* Root Cause & Evidence */}
          <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-xl space-y-2 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-[10px] text-indigo-300">Root Cause & Diagnostic Evidence</h4>
            <p className="text-slate-200 font-medium leading-relaxed">{plan.root_cause}</p>
            <p className="text-slate-400">Expected Impact: <strong className="text-emerald-300">{plan.expected_impact}</strong></p>
          </div>

          {/* Before vs Proposed After State Diff */}
          <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-xl space-y-2 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-[10px] text-indigo-300">Resource State Diff Comparison</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono">
              <div className="p-3 rounded bg-slate-900 border border-slate-800 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Before State</div>
                <div className="text-rose-400 text-[11px]">status: DEGRADED</div>
                <div className="text-rose-400 text-[11px]">health: UNHEALTHY</div>
                <div className="text-slate-400 text-[11px]">error_rate: 5.2%</div>
              </div>
              <div className="p-3 rounded bg-slate-900 border border-slate-800 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 uppercase">After / Target State</div>
                <div className="text-emerald-400 text-[11px]">status: HEALTHY</div>
                <div className="text-emerald-400 text-[11px]">health: OPERATIONAL</div>
                <div className="text-emerald-400 text-[11px]">error_rate: &lt; 1.0%</div>
              </div>
            </div>
          </div>

          {/* AI Explanation & Verification Plan */}
          <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-xl space-y-2 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-[10px] text-indigo-300">SRE Verification & Safety Guardrail Assessment</h4>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              <li>Idempotency protection enabled via execution key locking.</li>
              <li>5-minute resource cooldown window active to prevent remediation looping.</li>
              <li>15-minute telemetry verification window post-execution.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
