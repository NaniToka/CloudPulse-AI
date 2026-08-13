import React from "react";
import type { RemediationAction } from "@/types/finopsGovernance";
import { Play, Check, RotateCcw, AlertTriangle, ShieldCheck, DollarSign } from "lucide-react";

interface Props {
  remediations: RemediationAction[];
  loading: boolean;
  onApprove: (id: string, status: string) => Promise<void>;
  onExecute: (id: string, mode: string) => Promise<void>;
  onRollback: (id: string) => Promise<void>;
}

export const RemediationQueuePanel: React.FC<Props> = ({
  remediations,
  loading,
  onApprove,
  onExecute,
  onRollback,
}) => {
  const getApprovalBadge = (status: string) => {
    switch (status) {
      case "PENDING":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">PENDING APPROVAL</span>;
      case "APPROVED":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">APPROVED</span>;
      case "EXECUTED":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">EXECUTED (SIMULATED)</span>;
      case "ROLLED_BACK":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-500/10 text-slate-400 border border-slate-500/20">ROLLED BACK</span>;
      case "REJECTED":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">REJECTED</span>;
      default:
        return null;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-100">Controlled Remediation Queue</h3>
          <p className="text-xs text-slate-400">Approval workflow & automated rollback safeguard engine</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-slate-950 border border-slate-800 rounded text-[10px] font-mono text-emerald-400">
            DEMO / LOCAL MODE — Controlled Execution
          </span>
        </div>
      </div>

      {loading ? (
        <div className="space-y-3">
          <div className="h-16 bg-slate-800/60 rounded animate-pulse"></div>
          <div className="h-16 bg-slate-800/60 rounded animate-pulse"></div>
        </div>
      ) : remediations.length === 0 ? (
        <div className="py-10 text-center border border-dashed border-slate-800 rounded-lg">
          <ShieldCheck className="w-8 h-8 text-indigo-400 mx-auto mb-2 opacity-80" />
          <p className="text-sm font-medium text-slate-300">No active remediation requests in queue.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
          {remediations.map((rem) => (
            <div
              key={rem.id}
              className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl hover:border-slate-700/80 transition-colors space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg font-mono text-xs text-indigo-400">
                    {rem.provider.toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-slate-100">{rem.action_type.replace(/_/g, " ")}</span>
                      {getApprovalBadge(rem.approval_status)}
                    </div>
                    <span className="text-xs text-slate-400">Resource: <strong className="text-slate-200">{rem.resource_name}</strong></span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-bold text-emerald-400 block">${rem.estimated_savings.toLocaleString()}/mo Savings</span>
                  <span className="text-[10px] text-slate-500 capitalize">Risk: {rem.risk_level}</span>
                </div>
              </div>

              {rem.execution_result && (
                <div className="p-2.5 bg-slate-900/90 rounded border border-slate-800 text-[11px] font-mono text-slate-300">
                  {rem.execution_result}
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
                <span className="text-[11px] text-slate-400">Requested by: <span className="text-slate-300">{rem.requested_by}</span></span>

                <div className="flex items-center gap-2">
                  {rem.approval_status === "PENDING" && (
                    <>
                      <button
                        onClick={() => onApprove(rem.id, "REJECTED")}
                        className="px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 text-[11px] font-semibold transition-colors"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => onApprove(rem.id, "APPROVED")}
                        className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold transition-colors flex items-center gap-1 shadow-md shadow-emerald-500/20"
                      >
                        <Check className="w-3 h-3" /> Approve Action
                      </button>
                    </>
                  )}

                  {rem.approval_status === "APPROVED" && (
                    <button
                      onClick={() => onExecute(rem.id, "SIMULATED")}
                      className="px-3.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-semibold transition-colors flex items-center gap-1.5 shadow-md shadow-indigo-500/20"
                    >
                      <Play className="w-3 h-3" /> Execute (Simulated)
                    </button>
                  )}

                  {rem.approval_status === "EXECUTED" && (
                    <button
                      onClick={() => onRollback(rem.id)}
                      className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold transition-colors flex items-center gap-1 border border-slate-700"
                    >
                      <RotateCcw className="w-3 h-3 text-amber-400" /> Rollback Configuration
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
