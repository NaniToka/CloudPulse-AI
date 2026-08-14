import React, { useState } from 'react';
import { RemediationExecution } from '../../types/remediation';
import { RotateCcw, AlertCircle, ArrowLeftRight } from 'lucide-react';

interface RollbackCenterPanelProps {
  executions: RemediationExecution[];
  onRollback: (executionId: string) => Promise<void>;
}

export const RollbackCenterPanel: React.FC<RollbackCenterPanelProps> = ({ executions, onRollback }) => {
  const [rollingBackId, setRollingBackId] = useState<string | null>(null);

  const rollbackList = executions.filter(
    (e) => e.rollback_status === 'ROLLBACK_AVAILABLE' || e.status === 'ROLLED_BACK'
  );

  const handleTriggerRollback = async (id: string) => {
    setRollingBackId(id);
    try {
      await onRollback(id);
    } finally {
      setRollingBackId(null);
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <RotateCcw className="w-5 h-5 text-blue-400" />
          <h3 className="text-base font-bold text-white">Automated Rollback Center</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{rollbackList.length} Reversible Actions</span>
      </div>

      <div className="space-y-3">
        {rollbackList.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-500 bg-slate-800/40 rounded-xl border border-slate-700/50">
            No active actions with available rollback state diffs.
          </div>
        ) : (
          rollbackList.map((exc) => (
            <div
              key={exc.id}
              className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 font-mono text-xs">
                <div className="flex items-center gap-2 font-bold text-white">
                  <span>Execution ID: {exc.id.substring(0, 8)}...</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] ${
                      exc.status === 'ROLLED_BACK'
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    }`}
                  >
                    {exc.status}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-slate-300">
                  <span>Before State: {JSON.stringify(exc.previous_state || { status: 'DEGRADED' })}</span>
                  <ArrowLeftRight className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span>Changed State: {JSON.stringify(exc.new_state || { status: 'HEALTHY' })}</span>
                </div>
              </div>

              <div className="shrink-0">
                {exc.status === 'ROLLED_BACK' ? (
                  <span className="px-3 py-1 bg-slate-800 text-slate-400 text-xs font-bold rounded border border-slate-700">
                    Rolled Back
                  </span>
                ) : (
                  <button
                    onClick={() => handleTriggerRollback(exc.id)}
                    disabled={rollingBackId === exc.id}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-bold shadow transition-colors disabled:opacity-50"
                  >
                    <RotateCcw className={`w-3.5 h-3.5 ${rollingBackId === exc.id ? 'animate-spin' : ''}`} />
                    {rollingBackId === exc.id ? 'Rolling Back...' : 'Execute Rollback'}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
