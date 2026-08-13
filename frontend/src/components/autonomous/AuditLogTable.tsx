import React, { useState } from 'react';
import { RemediationAuditLog } from '../../types/autonomous';
import { FileText, Search, ShieldAlert, CheckCircle, Clock } from 'lucide-react';

interface AuditLogTableProps {
  logs: RemediationAuditLog[];
}

export const AuditLogTable: React.FC<AuditLogTableProps> = ({ logs }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = logs.filter(
    (log) =>
      log.action_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.target_resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.event_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Remediation Audit Trail</h3>
          <p className="text-xs text-slate-400">
            Immutable log of all remediation actions, approvals, state verifications, and rollbacks.
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search audit trail..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Event Type</th>
              <th className="py-3 px-4">Action & Resource</th>
              <th className="py-3 px-4">Provider</th>
              <th className="py-3 px-4">Mode</th>
              <th className="py-3 px-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No audit log entries recorded yet.
                </td>
              </tr>
            ) : (
              filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 font-semibold text-emerald-400">{log.event_type}</td>
                  <td className="py-3 px-4">
                    <div className="font-bold text-white font-mono">{log.action_type}</div>
                    <div className="text-[11px] text-slate-400">{log.target_resource}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{log.provider}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px]">
                      {log.execution_mode}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-[11px] text-slate-400 truncate max-w-xs">
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
