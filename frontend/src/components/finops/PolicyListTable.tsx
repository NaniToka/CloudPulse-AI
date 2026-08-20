import React from "react";
import type { CostPolicy } from "@/types/finopsGovernance";
import { Play, ToggleLeft, ToggleRight, Trash2, Filter, ShieldCheck } from "lucide-react";

interface Props {
  policies: CostPolicy[];
  loading: boolean;
  onToggleStatus: (id: string, currentEnabled: boolean) => Promise<void>;
  onEvaluate: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onOpenCreate: () => void;
}

export const PolicyListTable: React.FC<Props> = ({
  policies,
  loading,
  onToggleStatus,
  onEvaluate,
  onDelete,
  onOpenCreate,
}) => {
  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-orange-500/10 text-orange-400 border border-orange-500/20">HIGH</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-500/10 text-slate-400 border border-slate-500/20">{sev}</span>;
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 shadow-2xl backdrop-blur-xl space-y-4 relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 tracking-tight">FinOps Cost Policies</h3>
          <p className="text-xs text-slate-400">Configured spending rules & threshold guardrails</p>
        </div>
        <button
          onClick={onOpenCreate}
          className="px-3.5 py-1.5 text-xs font-bold font-mono rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/25"
        >
          + Build Policy
        </button>
      </div>

      {loading ? (
        <div className="space-y-2 py-4">
          <div className="h-10 bg-slate-800/60 rounded-xl animate-pulse"></div>
          <div className="h-10 bg-slate-800/60 rounded-xl animate-pulse"></div>
        </div>
      ) : policies.length === 0 ? (
        <div className="py-12 text-center border border-dashed border-slate-800 rounded-xl">
          <p className="text-sm text-slate-400 mb-2 font-sans">No cost policies configured.</p>
          <button
            onClick={onOpenCreate}
            className="text-xs font-bold text-indigo-400 hover:text-indigo-300 underline font-mono"
          >
            Create your first FinOps policy
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800/80">
          <table className="w-full text-left text-xs min-w-[700px]">
            <thead className="bg-slate-950/80 text-slate-400 uppercase font-bold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4 min-w-[180px]">Policy Name</th>
                <th className="py-3 px-4 min-w-[100px]">Category</th>
                <th className="py-3 px-4 min-w-[120px]">Provider / Scope</th>
                <th className="py-3 px-4 min-w-[160px]">Condition Rule</th>
                <th className="py-3 px-4 min-w-[90px]">Severity</th>
                <th className="py-3 px-4 text-center min-w-[90px]">Status</th>
                <th className="py-3 px-4 text-right min-w-[110px]">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
              {policies.map((policy) => (
                <tr key={policy.id} className="hover:bg-slate-900/60 transition-colors group">
                  <td className="py-3 px-4 font-semibold text-slate-200">
                    <div className="font-bold text-slate-100 text-xs">{policy.name}</div>
                    {policy.description && (
                      <div className="text-[11px] font-normal text-slate-400 truncate max-w-[220px]" title={policy.description}>
                        {policy.description}
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 font-bold uppercase">
                      {policy.category}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300 capitalize font-mono text-[11px]">
                    <span className="font-bold text-slate-200">{policy.provider}</span>{" "}
                    <span className="text-slate-400 font-normal text-[10px]">({policy.scope})</span>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-indigo-300">
                    {policy.metric} {policy.operator} ${policy.threshold_value.toLocaleString()}
                  </td>
                  <td className="py-3 px-4">{getSeverityBadge(policy.severity)}</td>
                  <td className="py-3 px-4 text-center">
                    <button
                      onClick={() => onToggleStatus(policy.id, policy.enabled)}
                      className="inline-flex items-center gap-1 font-medium transition-colors"
                      title={policy.enabled ? "Disable policy" : "Enable policy"}
                    >
                      {policy.enabled ? (
                        <>
                          <ToggleRight className="w-5 h-5 text-emerald-400" />
                          <span className="text-[10px] text-emerald-400 font-bold font-mono">ACTIVE</span>
                        </>
                      ) : (
                        <>
                          <ToggleLeft className="w-5 h-5 text-slate-500" />
                          <span className="text-[10px] text-slate-500 font-bold font-mono">DISABLED</span>
                        </>
                      )}
                    </button>
                  </td>
                  <td className="py-3 px-4 text-right space-x-1.5">
                    <button
                      onClick={() => onEvaluate(policy.id)}
                      className="px-2 py-1 text-[10px] font-bold font-mono rounded bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 transition-colors inline-flex items-center gap-1 border border-indigo-500/20"
                      title="Trigger Evaluation"
                    >
                      <Play className="w-3 h-3" /> Eval
                    </button>
                    <button
                      onClick={() => onDelete(policy.id)}
                      className="p-1 text-slate-500 hover:text-rose-400 transition-colors inline-flex items-center"
                      title="Delete Policy"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
