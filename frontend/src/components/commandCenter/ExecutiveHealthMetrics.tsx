import React from 'react';
import { ExecutiveHealth, OperationalRisk } from '../../types/commandCenter';
import { Activity, ShieldAlert, AlertCircle, ShieldCheck, DollarSign, PiggyBank, CheckCircle2 } from 'lucide-react';

interface ExecutiveHealthMetricsProps {
  health: ExecutiveHealth | null;
  risk: OperationalRisk | null;
  activeIncidentsCount: number;
  monthlySpend: number;
  potentialSavings: number;
}

export const ExecutiveHealthMetrics: React.FC<ExecutiveHealthMetricsProps> = ({
  health,
  risk,
  activeIncidentsCount,
  monthlySpend,
  potentialSavings,
}) => {
  if (!health || !risk) return null;

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'HEALTHY':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'DEGRADED':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
      case 'AT_RISK':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'CRITICAL':
      default:
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4">
      {/* 1. Overall Health Score */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Platform Health</span>
          <Activity className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-white font-mono">
          {health.overall_health_score} <span className="text-xs text-slate-500 font-sans">/ 100</span>
        </div>
        <div className="mt-1">
          <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold border ${getStatusBadge(health.status)}`}>
            {health.status}
          </span>
        </div>
      </div>

      {/* 2. Operational Risk Score */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Operational Risk</span>
          <ShieldAlert className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-2xl font-extrabold text-amber-400 font-mono">
          {risk.operational_risk_score} <span className="text-xs text-slate-500 font-sans">/ 100</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Risk Level: <strong className="text-amber-300">{risk.risk_level}</strong>
        </div>
      </div>

      {/* 3. Active Incidents */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Active Incidents</span>
          <AlertCircle className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-2xl font-extrabold text-rose-400 font-mono">
          {activeIncidentsCount}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          {health.active_breaches} active breaches
        </div>
      </div>

      {/* 4. SLO Compliance */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">SLO Compliance</span>
          <ShieldCheck className="w-4 h-4 text-blue-400" />
        </div>
        <div className="text-2xl font-extrabold text-white font-mono">
          {health.slo_compliance_pct}%
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Target: 99.9%
        </div>
      </div>

      {/* 5. Security Posture */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Security Score</span>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-emerald-400 font-mono">
          {health.security_score}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          CIS Compliance
        </div>
      </div>

      {/* 6. Monthly Cloud Spend */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Monthly Spend</span>
          <DollarSign className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="text-xl font-extrabold text-white font-mono">
          ${monthlySpend.toLocaleString()}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Cloud Infrastructure
        </div>
      </div>

      {/* 7. Potential Savings */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px] font-bold uppercase tracking-wider">Potential Savings</span>
          <PiggyBank className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-xl font-extrabold text-emerald-400 font-mono">
          ${potentialSavings.toLocaleString()}
        </div>
        <div className="text-[11px] text-slate-400 mt-1">
          Identified Waste
        </div>
      </div>
    </div>
  );
};
