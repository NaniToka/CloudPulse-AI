import React from 'react';
import { Bot, RefreshCw, Sparkles, ShieldCheck, Zap } from 'lucide-react';
import { RemediationFilterParams } from '../../services/remediationService';

interface RemediationHeaderProps {
  filters: RemediationFilterParams;
  onFilterChange: (filters: RemediationFilterParams) => void;
  onRefresh: () => void;
  onAnalyze: () => void;
  loading: boolean;
  analyzing: boolean;
}

export const RemediationHeader: React.FC<RemediationHeaderProps> = ({
  filters,
  onFilterChange,
  onRefresh,
  onAnalyze,
  loading,
  analyzing,
}) => {
  return (
    <div className="bg-slate-900/80 border border-indigo-500/30 rounded-xl p-5 shadow-xl backdrop-blur-md relative overflow-hidden">
      <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3.5 bg-indigo-500/15 border border-indigo-500/40 rounded-xl text-indigo-400">
            <Zap className="w-7 h-7 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold text-white tracking-tight">
                AIOps Action Center & Automated Remediation
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                DECIDE → EXECUTE
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Controlled operational remediation platform recommending, approving, executing & verifying self-healing actions.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
          {/* Status Filter */}
          <select
            value={filters.status || 'ALL'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                status: e.target.value === 'ALL' ? undefined : e.target.value,
              })
            }
            className="bg-slate-800/90 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="AWAITING_APPROVAL">AWAITING_APPROVAL</option>
            <option value="APPROVED">APPROVED</option>
            <option value="EXECUTING">EXECUTING</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="FAILED">FAILED</option>
            <option value="ROLLED_BACK">ROLLED_BACK</option>
          </select>

          {/* Provider Filter */}
          <select
            value={filters.provider || 'ALL'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                provider: e.target.value === 'ALL' ? undefined : e.target.value,
              })
            }
            className="bg-slate-800/90 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Providers</option>
            <option value="AWS">AWS</option>
            <option value="Kubernetes">Kubernetes</option>
            <option value="Azure">Azure</option>
            <option value="GCP">GCP</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={filters.risk_level || 'ALL'}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                risk_level: e.target.value === 'ALL' ? undefined : e.target.value,
              })
            }
            className="bg-slate-800/90 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">LOW Risk</option>
            <option value="MEDIUM">MEDIUM Risk</option>
            <option value="HIGH">HIGH Risk</option>
            <option value="CRITICAL">CRITICAL Risk</option>
          </select>

          {/* Analyze Button */}
          <button
            onClick={onAnalyze}
            disabled={analyzing}
            className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-indigo-950/50 transition-all disabled:opacity-50"
          >
            <Sparkles className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
            {analyzing ? 'Analyzing Remediation...' : 'Trigger AI Reasoning'}
          </button>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
};
