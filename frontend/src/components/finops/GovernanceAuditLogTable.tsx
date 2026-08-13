import React from "react";
import type { FinOpsAuditLog } from "@/types/finopsGovernance";
import { History, Activity } from "lucide-react";

interface Props {
  logs: FinOpsAuditLog[];
  loading: boolean;
}

export const GovernanceAuditLogTable: React.FC<Props> = ({ logs, loading }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-slate-800 text-slate-300 rounded-lg">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Governance Audit Trail</h3>
            <p className="text-xs text-slate-400">Immutable record of policy changes, approvals, and remediations</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="space-y-2">
          <div className="h-8 bg-slate-800/60 rounded animate-pulse"></div>
          <div className="h-8 bg-slate-800/60 rounded animate-pulse"></div>
        </div>
      ) : logs.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500">No audit activity recorded yet.</div>
      ) : (
        <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold text-[10px] tracking-wider border-b border-slate-800 sticky top-0 backdrop-blur">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Actor</th>
                <th className="py-2.5 px-4">Action</th>
                <th className="py-2.5 px-4">Entity</th>
                <th className="py-2.5 px-4">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-850/40 transition-colors">
                  <td className="py-2.5 px-4 text-slate-400">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="py-2.5 px-4 text-slate-200">{log.actor_email}</td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-semibold">{log.action}</span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-300">
                    {log.entity_type} <span className="text-slate-500 text-[10px]">({log.entity_id.slice(0, 8)})</span>
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">{log.result}</span>
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
