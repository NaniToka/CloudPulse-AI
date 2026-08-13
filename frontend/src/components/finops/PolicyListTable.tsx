import React from "react";
import type { CostPolicy } from "@/types/finopsGovernance";
import { Play, ToggleLeft, ToggleRight, Trash2, Filter } from "lucide-react";

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
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-100">FinOps Cost Policies</h3>
          <p className="text-xs text-slate-400">Configured spending rules & threshold guardrails</p>
        </div>
        <button
          onClick={onOpenCreate}
          className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-500/20"
        >
          + Build Cost Policy
        </button>
      </div>

      {loading ? (
        <div className="space-y-2 py-4">
          <div className="h-10 bg-slate-800/60 rounded animate-pulse"></div>
          <div className="h-10 bg-slate-800/60 rounded animate-pulse"></div>
        </div>
      ) : policies.length === 0 ? (
        <div className="py-12 text-center border border-dashed border-slate-800 rounded-lg">
          <p className="text-sm text-slate-400 mb-2">No cost policies configured.</p>
          <button
            onClick={onOpenCreate}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 underline"
          >
            Create your first FinOps policy
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Policy Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Provider / Scope</th>
                <th className="py-3 px-4">Condition Rule</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {policies.map((policy) => (
                <tr key={policy.id} className="hover:bg-slate-850/50 transition-colors group">
                  <td className="py-3 px-4 font-semibold text-slate-200">
                    <div>{policy.name}</div>
                    {policy.description && <div className="text-[11px] font-normal text-slate-400 truncate max-w-xs">{policy.description}</div>}
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">{policy.category}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-300 capitalize">
                    {policy.provider} <span className="text-slate-500 font-mono text-[10px]">({policy.scope})</span>
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
                          <span className="text-[10px] text-emerald-400">ACTIVE</span>
                        </>
                      ) : (
                        <>
                          <ToggleLeft className="w-5 h-5 text-slate-500" />
                          <span className="text-[10px] text-slate-500">DISABLED</span>
                        </>
                      )}
                    </button>
                  </td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <button
                      onClick={() => onEvaluate(policy.id)}
                      className="px-2.5 py-1 text-[11px] font-medium rounded bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 transition-colors inline-flex items-center gap-1"
                      title="Trigger Evaluation"
                    >
                      <Play className="w-3 h-3" /> Evaluate
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
