import React from 'react';
import { Server, DollarSign, AlertTriangle, ShieldAlert, CheckCircle2, TrendingUp, Layers } from 'lucide-react';
import { AssetOverviewResponse } from '../../types/assets';

interface AssetOverviewCardsProps {
  overview?: AssetOverviewResponse | null;
}

export const AssetOverviewCards: React.FC<AssetOverviewCardsProps> = ({ overview }) => {
  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      {/* Total Resources */}
      <div className="group relative bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-indigo-500/40 rounded-2xl p-5 shadow-xl hover:shadow-indigo-500/10 transition-all duration-300 overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-all" />
        <div className="flex items-center justify-between relative z-10">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Cloud Assets</span>
          <div className="p-2.5 bg-indigo-500/10 rounded-xl text-indigo-400 border border-indigo-500/20 shadow-[0_0_12px_rgba(99,102,241,0.15)]">
            <Server className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 flex items-baseline justify-between relative z-10">
          <span className="text-3xl font-extrabold text-slate-100 tracking-tight">{overview.total_resources}</span>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-400 border border-slate-700/80">
            4 Platforms
          </span>
        </div>
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 relative z-10">
          <div className="flex items-center gap-2">
            <span className="text-amber-400 font-semibold">AWS: {overview.aws_count}</span>
            <span>•</span>
            <span className="text-sky-400 font-semibold">AZ: {overview.azure_count}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-emerald-400 font-semibold">GCP: {overview.gcp_count}</span>
            <span>•</span>
            <span className="text-purple-400 font-semibold">K8s: {overview.kubernetes_count}</span>
          </div>
        </div>
      </div>

      {/* Monthly Cost & Savings */}
      <div className="group relative bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-emerald-500/40 rounded-2xl p-5 shadow-xl hover:shadow-emerald-500/10 transition-all duration-300 overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-all" />
        <div className="flex items-center justify-between relative z-10">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Monthly Cost Burn</span>
          <div className="p-2.5 bg-emerald-500/10 rounded-xl text-emerald-400 border border-emerald-500/20 shadow-[0_0_12px_rgba(16,185,129,0.15)]">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 flex items-baseline justify-between relative z-10">
          <span className="text-3xl font-extrabold text-slate-100 tracking-tight">${overview.total_monthly_cost.toLocaleString()}</span>
          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            +${overview.total_potential_savings.toLocaleString()} savings
          </span>
        </div>
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 relative z-10">
          <span>FinOps Engine Active</span>
          <span className="text-emerald-400 font-semibold">Orphaned: {overview.orphaned_count}</span>
        </div>
      </div>

      {/* Health Status */}
      <div className="group relative bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-sky-500/40 rounded-2xl p-5 shadow-xl hover:shadow-sky-500/10 transition-all duration-300 overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-sky-500/5 rounded-full blur-2xl group-hover:bg-sky-500/10 transition-all" />
        <div className="flex items-center justify-between relative z-10">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Health Posture</span>
          <div className="p-2.5 bg-sky-500/10 rounded-xl text-sky-400 border border-sky-500/20 shadow-[0_0_12px_rgba(14,165,233,0.15)]">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 flex items-baseline justify-between relative z-10">
          <span className="text-3xl font-extrabold text-slate-100 tracking-tight">{overview.healthy_count} <span className="text-sm font-semibold text-emerald-400">Healthy</span></span>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {overview.warning_count} Warning
          </span>
        </div>
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 relative z-10">
          <span>Critical / Degraded</span>
          <span className="text-rose-400 font-bold">{overview.critical_count} critical</span>
        </div>
      </div>

      {/* Waste & Risk */}
      <div className="group relative bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-amber-500/40 rounded-2xl p-5 shadow-xl hover:shadow-amber-500/10 transition-all duration-300 overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl group-hover:bg-amber-500/10 transition-all" />
        <div className="flex items-center justify-between relative z-10">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Unutilized / Waste</span>
          <div className="p-2.5 bg-amber-500/10 rounded-xl text-amber-400 border border-amber-500/20 shadow-[0_0_12px_rgba(245,158,11,0.15)]">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 flex items-baseline justify-between relative z-10">
          <span className="text-3xl font-extrabold text-amber-400 tracking-tight">{overview.orphaned_count + overview.idle_count}</span>
          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            Actionable Risk
          </span>
        </div>
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 relative z-10">
          <span>Orphaned Storage & Compute</span>
          <span className="text-slate-200 font-bold">{overview.idle_count} Idle</span>
        </div>
      </div>
    </div>
  );
};
