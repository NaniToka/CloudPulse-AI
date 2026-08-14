import React from 'react';
import { RemediationPlan } from '../../types/remediation';
import { History, CheckCircle2, AlertTriangle, RotateCcw } from 'lucide-react';

interface RemediationHistoryTableProps {
  plans: RemediationPlan[];
  onSelectPlan: (plan: RemediationPlan) => void;
  onExecute: (planId: string) => Promise<void>;
}

export const RemediationHistoryTable: React.FC<RemediationHistoryTableProps> = ({
  plans,
  onSelectPlan,
  onExecute,
}) => {
  const historyPlans = plans.filter((p) =>
    ['APPROVED', 'COMPLETED', 'SUCCEEDED', 'FAILED', 'ROLLED_BACK', 'REJECTED'].includes(p.status.toUpperCase())
  );

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'SUCCEEDED':
      case 'COMPLETED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'APPROVED':
        return 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30';
      case 'ROLLED_BACK':
        return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
      case 'FAILED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'REJECTED':
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Remediation Action History</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{historyPlans.length} Executed / Resolved Records</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Action</th>
              <th className="py-3 px-4">Target Resource</th>
              <th className="py-3 px-4">Risk</th>
              <th className="py-3 px-4">Mode</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {historyPlans.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No historical remediation action records found.
                </td>
              </tr>
            ) : (
              historyPlans.map((p) => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors cursor-pointer" onClick={() => onSelectPlan(p)}>
                  <td className="py-3.5 px-4 font-mono text-slate-400">
                    {new Date(p.created_at).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 font-mono font-bold text-white">{p.action_type}</td>
                  <td className="py-3.5 px-4 font-mono text-indigo-300">{p.affected_resource}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">{p.risk_level}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">{p.execution_mode}</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2.5 py-1 rounded text-[10px] font-extrabold border ${getStatusBadge(p.status)}`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right shrink-0" onClick={(e) => e.stopPropagation()}>
                    {p.status === 'APPROVED' && (
                      <button
                        onClick={() => onExecute(p.id)}
                        className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[11px] font-bold transition-colors shadow"
                      >
                        Execute
                      </button>
                    )}
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
