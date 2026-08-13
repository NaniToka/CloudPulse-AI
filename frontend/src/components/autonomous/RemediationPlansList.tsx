import React from 'react';
import { RemediationPlan } from '../../types/autonomous';
import { Play, CheckCircle, RotateCcw, AlertOctagon, Clock, ShieldCheck } from 'lucide-react';

interface RemediationPlansListProps {
  plans: RemediationPlan[];
  onApprove: (planId: string) => void;
  onExecute: (planId: string) => void;
  onRollback: (planId: string) => void;
}

export const RemediationPlansList: React.FC<RemediationPlansListProps> = ({
  plans,
  onApprove,
  onExecute,
  onRollback,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'COMPLETED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'APPROVED':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'WAITING_APPROVAL':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'EXECUTING':
      case 'VERIFYING':
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 animate-pulse';
      case 'ROLLED_BACK':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'FAILED':
      case 'BLOCKED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Active & Historical Remediation Plans</h3>
          <p className="text-xs text-slate-400">
            Generated remediation plans with confidence scores, impact estimates, and execution controls.
          </p>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Total Plans: {plans.length}</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Action & Resource</th>
              <th className="py-3 px-4">Root Cause</th>
              <th className="py-3 px-4">Risk & Impact</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Mode</th>
              <th className="py-3 px-4 text-right">Action Control</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {plans.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No remediation plans registered yet. Click 'Simulate' or trigger an incident signal to generate plans.
                </td>
              </tr>
            ) : (
              plans.map((plan) => (
                <tr key={plan.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-bold text-white font-mono">{plan.action_type}</div>
                    <div className="text-[11px] text-slate-400">{plan.affected_resource} ({plan.provider})</div>
                  </td>
                  <td className="py-3 px-4 text-slate-300 max-w-xs truncate font-medium">
                    {plan.root_cause}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="text-[10px] font-bold text-slate-300">{plan.risk_level} RISK</span>
                    </div>
                    <div className="text-[10px] text-slate-400 truncate max-w-xs">{plan.expected_impact}</div>
                  </td>
                  <td className="py-3 px-4 font-semibold text-emerald-400">
                    {(plan.confidence_score * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getStatusBadge(
                        plan.status
                      )}`}
                    >
                      {plan.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px]">
                      {plan.execution_mode}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {plan.status === 'WAITING_APPROVAL' || plan.status === 'PLANNED' ? (
                        <button
                          onClick={() => onApprove(plan.id)}
                          className="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold transition-colors flex items-center gap-1"
                        >
                          <ShieldCheck className="w-3 h-3" /> Approve
                        </button>
                      ) : null}

                      {plan.status === 'APPROVED' ? (
                        <button
                          onClick={() => onExecute(plan.id)}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold transition-colors flex items-center gap-1"
                        >
                          <Play className="w-3 h-3" /> Execute
                        </button>
                      ) : null}

                      {plan.status === 'COMPLETED' && plan.rollback_supported ? (
                        <button
                          onClick={() => onRollback(plan.id)}
                          className="px-2 py-1 bg-purple-950/60 hover:bg-purple-900/60 text-purple-300 border border-purple-700/50 rounded text-xs font-semibold transition-colors flex items-center gap-1"
                        >
                          <RotateCcw className="w-3 h-3" /> Rollback
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
