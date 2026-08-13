import React from 'react';
import { SloOverview } from '../../types/slo';
import { ShieldCheck, AlertTriangle, AlertCircle, PieChart, Activity, CheckCircle2 } from 'lucide-react';

interface ReliabilityOverviewHeaderProps {
  overview: SloOverview | null;
}

export const ReliabilityOverviewHeader: React.FC<ReliabilityOverviewHeaderProps> = ({ overview }) => {
  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* 1. Overall Reliability Score */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Reliability Score</span>
          <Activity className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-bold text-white font-mono">
          {overview.platform_reliability_score} <span className="text-xs text-slate-400 font-sans">/ 100</span>
        </div>
        <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3" /> Platform Healthy
        </div>
      </div>

      {/* 2. SLO Compliance % */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">SLO Compliance</span>
          <ShieldCheck className="w-4 h-4 text-blue-400" />
        </div>
        <div className="text-2xl font-bold text-white font-mono">
          {overview.slo_compliance_pct}%
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {overview.healthy_services} of {overview.total_services} services meeting SLO
        </div>
      </div>

      {/* 3. Services At Risk */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Services At Risk</span>
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-2xl font-bold text-amber-400 font-mono">
          {overview.at_risk_services}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Elevated burn rates detected
        </div>
      </div>

      {/* 4. Active Violations */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Active Violations</span>
          <AlertCircle className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-2xl font-bold text-rose-400 font-mono">
          {overview.active_violations}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {overview.breached_services} breached services
        </div>
      </div>

      {/* 5. Error Budget Remaining */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Budget Remaining</span>
          <PieChart className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="text-2xl font-bold text-indigo-300 font-mono">
          {overview.average_error_budget_remaining_pct}%
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          30-day rolling window avg
        </div>
      </div>
    </div>
  );
};
