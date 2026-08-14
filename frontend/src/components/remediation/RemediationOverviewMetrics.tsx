import React from 'react';
import { RemediationOverview } from '../../types/remediation';
import { Clock, Activity, CheckCircle2, AlertTriangle, RotateCcw, ShieldCheck } from 'lucide-react';

interface RemediationOverviewMetricsProps {
  overview: RemediationOverview | null;
}

export const RemediationOverviewMetrics: React.FC<RemediationOverviewMetricsProps> = ({ overview }) => {
  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      {/* 1. Pending Approvals */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Pending Approvals</span>
          <Clock className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-2xl font-extrabold text-amber-400 font-mono">
          {overview.pending_approvals_count}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Awaiting Human Review</div>
      </div>

      {/* 2. Active Executions */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Active Executions</span>
          <Activity className="w-4 h-4 text-indigo-400 animate-pulse" />
        </div>
        <div className="text-2xl font-extrabold text-indigo-300 font-mono">
          {overview.active_executions_count}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">In Execution / Verifying</div>
      </div>

      {/* 3. Successful Remediations */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Successful Actions</span>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-emerald-400 font-mono">
          {overview.completed_remediations_count}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Verified & Resolved</div>
      </div>

      {/* 4. Failed Remediations */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Failed Actions</span>
          <AlertTriangle className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-2xl font-extrabold text-rose-400 font-mono">
          {overview.failed_remediations_count}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Execution Failures</div>
      </div>

      {/* 5. Rollback Available */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Rollback Available</span>
          <RotateCcw className="w-4 h-4 text-blue-400" />
        </div>
        <div className="text-2xl font-extrabold text-blue-300 font-mono">
          {overview.rollback_available_count}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Reversible State Diffs</div>
      </div>

      {/* 6. Success Rate */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Automation Success</span>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-white font-mono">
          {overview.success_rate_pct}%
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Verified Resolution Rate</div>
      </div>
    </div>
  );
};
