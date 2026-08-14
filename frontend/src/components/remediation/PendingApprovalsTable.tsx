import React, { useState } from 'react';
import { RemediationPlan } from '../../types/remediation';
import { Clock, Check, X, Eye, Play, ShieldAlert } from 'lucide-react';

interface PendingApprovalsTableProps {
  plans: RemediationPlan[];
  onApprove: (planId: string, comments?: string) => Promise<void>;
  onReject: (planId: string, reason: string) => Promise<void>;
  onDryRun: (planId: string) => Promise<void>;
  onSelectPlan: (plan: RemediationPlan) => void;
}

export const PendingApprovalsTable: React.FC<PendingApprovalsTableProps> = ({
  plans,
  onApprove,
  onReject,
  onDryRun,
  onSelectPlan,
}) => {
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [comments, setComments] = useState<string>('');
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [modalMode, setModalMode] = useState<'APPROVE' | 'REJECT' | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const pendingPlans = plans.filter((p) =>
    ['AWAITING_APPROVAL', 'RECOMMENDED', 'PLANNED'].includes(p.status.toUpperCase())
  );

  const handleConfirmApprove = async () => {
    if (!selectedPlanId) return;
    setSubmitting(true);
    try {
      await onApprove(selectedPlanId, comments);
      setModalMode(null);
      setSelectedPlanId(null);
      setComments('');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmReject = async () => {
    if (!selectedPlanId || !rejectionReason.trim()) return;
    setSubmitting(true);
    try {
      await onReject(selectedPlanId, rejectionReason);
      setModalMode(null);
      setSelectedPlanId(null);
      setRejectionReason('');
    } finally {
      setSubmitting(false);
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'LOW':
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-bold text-white">Pending Remediation Approvals Queue</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{pendingPlans.length} Awaiting Approval</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Action</th>
              <th className="py-3 px-4">Target Resource</th>
              <th className="py-3 px-4">Risk Level</th>
              <th className="py-3 px-4">Trigger / Root Cause</th>
              <th className="py-3 px-4">Provider</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {pendingPlans.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No remediation actions awaiting approval.
                </td>
              </tr>
            ) : (
              pendingPlans.map((p) => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors cursor-pointer" onClick={() => onSelectPlan(p)}>
                  <td className="py-3.5 px-4 font-mono font-bold text-white">{p.action_type}</td>
                  <td className="py-3.5 px-4 font-mono text-indigo-300">{p.affected_resource}</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold border ${getRiskBadge(p.risk_level)}`}>
                      {p.risk_level}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300 max-w-xs truncate">{p.root_cause}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">{p.provider}</td>
                  <td className="py-3.5 px-4 font-mono font-semibold text-amber-300">{p.status}</td>
                  <td className="py-3.5 px-4 text-right space-x-2 shrink-0" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => onDryRun(p.id)}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-bold transition-colors"
                    >
                      Dry Run
                    </button>

                    <button
                      onClick={() => {
                        setSelectedPlanId(p.id);
                        setModalMode('APPROVE');
                      }}
                      className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[11px] font-bold transition-colors"
                    >
                      Approve
                    </button>

                    <button
                      onClick={() => {
                        setSelectedPlanId(p.id);
                        setModalMode('REJECT');
                      }}
                      className="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-[11px] font-bold transition-colors"
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Approve Modal */}
      {modalMode === 'APPROVE' && selectedPlanId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Check className="w-5 h-5 text-emerald-400" /> Approve Remediation Plan
            </h3>
            <p className="text-xs text-slate-400">
              Confirm approval to authorize execution. Action will run in local simulation mode.
            </p>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Optional approval comment..."
              className="w-full bg-slate-800 border border-slate-700 text-xs text-white rounded-lg p-3 focus:outline-none focus:border-indigo-500"
              rows={3}
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setModalMode(null)}
                className="px-4 py-2 bg-slate-800 text-slate-300 text-xs rounded-lg font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmApprove}
                disabled={submitting}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs rounded-lg font-bold disabled:opacity-50"
              >
                {submitting ? 'Approving...' : 'Confirm Approve'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {modalMode === 'REJECT' && selectedPlanId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <X className="w-5 h-5 text-rose-400" /> Reject Remediation Plan
            </h3>
            <p className="text-xs text-slate-400">Specify rejection rationale before rejecting this action request.</p>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Rejection rationale (required)..."
              className="w-full bg-slate-800 border border-slate-700 text-xs text-white rounded-lg p-3 focus:outline-none focus:border-rose-500"
              rows={3}
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setModalMode(null)}
                className="px-4 py-2 bg-slate-800 text-slate-300 text-xs rounded-lg font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmReject}
                disabled={submitting || !rejectionReason.trim()}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs rounded-lg font-bold disabled:opacity-50"
              >
                {submitting ? 'Rejecting...' : 'Confirm Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
