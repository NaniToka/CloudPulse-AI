import React from "react";
import type { CostViolation } from "@/types/finopsGovernance";
import { AlertCircle, CheckCircle, ShieldAlert, Clock, ArrowRight } from "lucide-react";

interface Props {
  violations: CostViolation[];
  loading: boolean;
  onUpdateStatus: (id: string, newStatus: string) => Promise<void>;
  onRequestRemediation: (viol: CostViolation) => void;
}

export const ViolationListPanel: React.FC<Props> = ({
  violations,
  loading,
  onUpdateStatus,
  onRequestRemediation,
}) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "OPEN":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">OPEN</span>;
      case "ACKNOWLEDGED":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">ACKNOWLEDGED</span>;
      case "IN_REVIEW":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">IN REVIEW</span>;
      case "RESOLVED":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">RESOLVED</span>;
      case "EXEMPTED":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-500/10 text-slate-400 border border-slate-500/20">EXEMPTED</span>;
      default:
        return null;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-100">Policy Violation Center</h3>
          <p className="text-xs text-slate-400">Non-compliant spending breaches requiring remediation</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
          {violations.filter((v) => v.status === "OPEN").length} Open Violations
        </span>
      </div>

      {loading ? (
        <div className="space-y-3">
          <div className="h-16 bg-slate-800/60 rounded animate-pulse"></div>
          <div className="h-16 bg-slate-800/60 rounded animate-pulse"></div>
        </div>
      ) : violations.length === 0 ? (
        <div className="py-12 text-center border border-dashed border-slate-800 rounded-lg">
          <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-80" />
          <p className="text-sm font-medium text-slate-300">All cost policies fully compliant!</p>
          <p className="text-xs text-slate-500">No active spending violations detected.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
          {violations.map((viol) => (
            <div
              key={viol.id}
              className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl hover:border-slate-700/80 transition-colors space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-sm text-slate-100">{viol.policy_name}</span>
                    {getStatusBadge(viol.status)}
                  </div>
                  <p className="text-xs text-slate-300">{viol.explanation}</p>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-xs font-bold text-rose-400 block">+${viol.difference.toLocaleString()} Over</span>
                  <span className="text-[10px] text-slate-500 font-mono">Actual: ${viol.actual_value.toLocaleString()}</span>
                </div>
              </div>

              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs">
                <div className="space-y-0.5">
                  <span className="text-[10px] uppercase font-bold text-indigo-400 block">Recommended Action</span>
                  <p className="text-slate-300">{viol.recommended_action}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-4">
                  <select
                    value={viol.status}
                    onChange={(e) => onUpdateStatus(viol.id, e.target.value)}
                    className="bg-slate-950 border border-slate-800 text-slate-300 rounded px-2 py-1 text-[11px] focus:outline-none"
                  >
                    <option value="OPEN">OPEN</option>
                    <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                    <option value="IN_REVIEW">IN_REVIEW</option>
                    <option value="RESOLVED">RESOLVED</option>
                    <option value="EXEMPTED">EXEMPTED</option>
                  </select>
                  <button
                    onClick={() => onRequestRemediation(viol)}
                    className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[11px] font-semibold transition-colors flex items-center gap-1 shadow-md shadow-indigo-500/20"
                  >
                    Remediate <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
