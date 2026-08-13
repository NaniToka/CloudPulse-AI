import React from 'react';
import { RemediationExecution } from '../../types/autonomous';
import { Lock, RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface ExecutionQueueStatusProps {
  queue: RemediationExecution[];
}

export const ExecutionQueueStatus: React.FC<ExecutionQueueStatusProps> = ({ queue }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <h3 className="text-base font-semibold text-white">Active Execution Queue & Resource Locks</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Active Jobs: {queue.length}</span>
      </div>

      {queue.length === 0 ? (
        <div className="p-6 text-center border border-dashed border-slate-800 rounded-lg bg-slate-900/30">
          <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-80" />
          <div className="text-xs font-semibold text-slate-300">Execution Queue Clear</div>
          <p className="text-[11px] text-slate-500 mt-0.5">No active concurrency locks or executing remediation jobs.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {queue.map((exec) => (
            <div
              key={exec.id}
              className="p-3.5 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-white font-mono">{exec.idempotency_key}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-2">
                    <span>Mode: <strong className="text-emerald-400">{exec.execution_mode}</strong></span>
                    <span>•</span>
                    <span>Started: {exec.started_at ? new Date(exec.started_at).toLocaleTimeString() : 'Queued'}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 animate-pulse">
                  {exec.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
