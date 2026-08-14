import React from 'react';
import { Server, DollarSign, AlertTriangle, ShieldAlert, CheckCircle2, AlertCircle } from 'lucide-react';
import { AssetOverviewResponse } from '../../types/assets';

interface AssetOverviewCardsProps {
  overview?: AssetOverviewResponse | null;
}

export const AssetOverviewCards: React.FC<AssetOverviewCardsProps> = ({ overview }) => {
  if (!overview) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Total Resources */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Cloud Assets</span>
          <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
            <Server className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-3xl font-bold text-slate-100">{overview.total_resources}</span>
          <span className="text-xs text-slate-400">across 4 platforms</span>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>AWS: {overview.aws_count} | Azure: {overview.azure_count}</span>
          <span>GCP: {overview.gcp_count} | K8s: {overview.kubernetes_count}</span>
        </div>
      </div>

      {/* Monthly Cost & Savings */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Monthly Cost Burn</span>
          <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-3xl font-bold text-slate-100">${overview.total_monthly_cost.toLocaleString()}</span>
          <span className="text-xs text-emerald-400 font-medium">${overview.total_potential_savings.toLocaleString()} savings</span>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>FinOps Cost Integrated</span>
          <span className="text-emerald-400 font-medium">Orphaned: {overview.orphaned_count}</span>
        </div>
      </div>

      {/* Health Status */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Health Posture</span>
          <div className="p-2 bg-sky-500/10 rounded-lg text-sky-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-3xl font-bold text-slate-100">{overview.healthy_count} <span className="text-sm font-normal text-slate-400">Healthy</span></span>
          <span className="text-xs text-amber-400 font-medium">{overview.warning_count} Warning</span>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>Critical / Degraded</span>
          <span className="text-rose-400 font-semibold">{overview.critical_count} critical</span>
        </div>
      </div>

      {/* Waste & Risk */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Unutilized / Waste</span>
          <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-3xl font-bold text-amber-400">{overview.orphaned_count + overview.idle_count}</span>
          <span className="text-xs text-amber-400 font-medium">Actionable</span>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>Orphaned Storage & Compute</span>
          <span className="text-slate-300 font-semibold">{overview.idle_count} Idle</span>
        </div>
      </div>
    </div>
  );
};
