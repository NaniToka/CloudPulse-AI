import React from 'react';
import { AlertCircle, ShieldAlert, DollarSign, PiggyBank, PieChart, Activity, AlertOctagon, Server } from 'lucide-react';
import { KeyExecutiveMetricsResponse } from '../../types/executive';

interface Props {
  metrics: KeyExecutiveMetricsResponse;
}

export const KeyMetricsGrid: React.FC<Props> = ({ metrics }) => {
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  const items = [
    {
      title: 'Active Incidents',
      value: `${metrics.active_incidents}`,
      subtext: `${metrics.critical_incidents} Critical P1`,
      icon: AlertCircle,
      color: metrics.critical_incidents > 0 ? 'text-rose-400 border-rose-500/30 bg-rose-500/10 shadow-[0_0_10px_rgba(244,63,94,0.15)]' : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    },
    {
      title: 'Critical Security Findings',
      value: `${metrics.critical_security_findings}`,
      subtext: `${metrics.security_findings} Scanned Findings`,
      icon: ShieldAlert,
      color: metrics.critical_security_findings > 0 ? 'text-amber-400 border-amber-500/30 bg-amber-500/10 shadow-[0_0_10px_rgba(245,158,11,0.15)]' : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    },
    {
      title: 'Monthly Spend',
      value: formatCurrency(metrics.current_monthly_spend),
      subtext: `Projected: ${formatCurrency(metrics.projected_spend)}`,
      icon: DollarSign,
      color: 'text-indigo-400 border-indigo-500/30 bg-indigo-500/10 shadow-[0_0_10px_rgba(99,102,241,0.15)]',
    },
    {
      title: 'Potential Savings',
      value: formatCurrency(metrics.potential_savings),
      subtext: 'FinOps Identified',
      icon: PiggyBank,
      color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10 shadow-[0_0_10px_rgba(16,185,129,0.15)]',
    },
    {
      title: 'Budget Utilization',
      value: `${metrics.budget_utilization_pct}%`,
      subtext: 'Monthly Allocated',
      icon: PieChart,
      color: metrics.budget_utilization_pct > 90 ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' : 'text-sky-400 border-sky-500/30 bg-sky-500/10',
    },
    {
      title: 'Policy Violations',
      value: `${metrics.policy_violations}`,
      subtext: `${metrics.pending_remediations} Pending Actions`,
      icon: AlertOctagon,
      color: metrics.policy_violations > 0 ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    },
    {
      title: 'Capacity Risk Score',
      value: `${metrics.capacity_risk_score}`,
      subtext: '100 Max Scale',
      icon: Activity,
      color: metrics.capacity_risk_score > 50 ? 'text-amber-400 border-amber-500/30 bg-amber-500/10' : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    },
    {
      title: 'Unhealthy Services',
      value: `${metrics.unhealthy_services}`,
      subtext: `K8s Risk: ${metrics.kubernetes_risk_level}`,
      icon: Server,
      color: metrics.unhealthy_services > 0 ? 'text-rose-400 border-rose-500/30 bg-rose-500/10' : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {items.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div
            key={idx}
            className="p-5 bg-slate-900/70 border border-slate-800/80 hover:border-slate-700/80 rounded-2xl backdrop-blur-xl transition-all duration-200 shadow-xl hover:shadow-2xl flex flex-col justify-between"
          >
            <div className="flex items-center justify-between gap-2 mb-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider truncate">{item.title}</span>
              <div className={`p-2 rounded-xl border ${item.color} shrink-0`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-extrabold text-slate-100 tracking-tight mb-1">{item.value}</div>
              <div className="text-xs text-slate-400 font-medium">{item.subtext}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
