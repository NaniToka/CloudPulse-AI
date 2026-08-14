import React from 'react';
import { RemediationAuditItem } from '../../types/remediation';
import { ShieldCheck, FileText } from 'lucide-react';

interface AuditTrailTableProps {
  auditLogs: RemediationAuditItem[];
}

export const AuditTrailTable: React.FC<AuditTrailTableProps> = ({ auditLogs }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Immutable Remediation Audit Log Trail</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{auditLogs.length} Security Audit Events</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Event Type</th>
              <th className="py-3 px-4">Action Type</th>
              <th className="py-3 px-4">Target Resource</th>
              <th className="py-3 px-4">Provider</th>
              <th className="py-3 px-4">Execution Mode</th>
              <th className="py-3 px-4">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {auditLogs.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No security audit log entries recorded yet.
                </td>
              </tr>
            ) : (
              auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-mono text-slate-400">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 font-mono font-bold text-indigo-300">{log.event_type}</td>
                  <td className="py-3.5 px-4 font-mono font-bold text-white">{log.action_type}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">{log.target_resource}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400">{log.provider}</td>
                  <td className="py-3.5 px-4 font-mono text-amber-300">{log.execution_mode}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-400 text-[11px] max-w-xs truncate">
                    {JSON.stringify(log.details)}
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
