import React from 'react';
import { RemediationExecution } from '../../types/remediation';
import { Activity, RefreshCw } from 'lucide-react';

interface ActiveExecutionsPanelProps {
  executions: RemediationExecution[];
}

export const ActiveExecutionsPanel: React.FC<ActiveExecutionsPanelProps> = ({ executions }) => {
  const activeList = executions.filter((e) =>
    ['QUEUED', 'VALIDATING', 'EXECUTING', 'VERIFYING'].includes(e.status.toUpperCase())
  );

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400 animate-pulse" />
          <h3 className="text-base font-bold text-white">Active Remediation Executions Stream</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{activeList.length} In-Flight</span>
      </div>

      <div className="space-y-3">
        {activeList.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-500 bg-slate-800/40 rounded-xl border border-slate-700/50">
            No active remediation executions currently running.
          </div>
        ) : (
          activeList.map((exc) => (
            <div
              key={exc.id}
              className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2 font-mono font-bold text-white text-xs">
                  <span>Execution ID: {exc.id.substring(0, 8)}...</span>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                    {exc.execution_mode}
                  </span>
                </div>
                <div className="text-xs text-slate-300 font-mono">
                  Idempotency Key: {exc.idempotency_key}
                </div>
              </div>

              <div className="flex items-center gap-2 font-mono text-xs font-bold text-indigo-400">
                <RefreshCw className="w-4 h-4 animate-spin" />
                {exc.status}...
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
