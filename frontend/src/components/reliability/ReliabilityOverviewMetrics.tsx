import React from 'react';
import { ReliabilityOverview } from '../../types/reliability';
import { ShieldCheck, AlertTriangle, Flame, Activity, PieChart, CheckCircle2 } from 'lucide-react';

interface ReliabilityOverviewMetricsProps {
  overview: ReliabilityOverview | null;
}

export const ReliabilityOverviewMetrics: React.FC<ReliabilityOverviewMetricsProps> = ({ overview }) => {
  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      {/* 1. Overall Reliability Score */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Overall Reliability Score</span>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-white font-mono">
          {overview.overall_reliability_score} <span className="text-xs text-slate-500 font-sans">/ 100</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Platform SRE Score</div>
      </div>

      {/* 2. Services Healthy */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Services Healthy</span>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-emerald-400 font-mono">
          {overview.services_healthy}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Within Target SLO</div>
      </div>

      {/* 3. Services At Risk */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Services At Risk</span>
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-2xl font-extrabold text-amber-400 font-mono">
          {overview.services_at_risk}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Elevated Burn / Risk</div>
      </div>

      {/* 4. SLO Breaches */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">SLO Breaches</span>
          <AlertTriangle className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-2xl font-extrabold text-rose-400 font-mono">
          {overview.services_breached}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Active SLO Breaches</div>
      </div>

      {/* 5. Critical Burn Rates */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Critical Burn Rates</span>
          <Flame className="w-4 h-4 text-rose-400 animate-pulse" />
        </div>
        <div className="text-2xl font-extrabold text-rose-400 font-mono">
          {overview.critical_burn_rates_count}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">&gt; 3.0x Burn Rate</div>
      </div>

      {/* 6. Error Budget Remaining */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Error Budget Remaining</span>
          <PieChart className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="text-2xl font-extrabold text-indigo-300 font-mono">
          {overview.error_budget_remaining_pct}%
        </div>
        <div className="text-[11px] text-slate-400 mt-1">Platform Average</div>
      </div>
    </div>
  );
};
