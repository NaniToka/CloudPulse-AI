import React from 'react';
import { Cloud, Box, CheckCircle2, AlertTriangle, TrendingUp } from 'lucide-react';

export const CloudProviderHealthCard: React.FC = () => {
  const providers = [
    { provider: 'AWS', health: 'HEALTHY', risk: 'LOW', costTrend: '+2.4%', activeIssues: 2, region: 'us-east-1' },
    { provider: 'Azure', health: 'HEALTHY', risk: 'LOW', costTrend: '-1.1%', activeIssues: 0, region: 'eastus' },
    { provider: 'GCP', health: 'HEALTHY', risk: 'LOW', costTrend: '+0.5%', activeIssues: 0, region: 'us-central1' },
    { provider: 'Kubernetes (EKS)', health: 'AT_RISK', risk: 'MEDIUM', costTrend: '+4.8%', activeIssues: 1, region: 'prod-primary' },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Cloud className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Multi-Cloud & Kubernetes Infrastructure Health</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Active Providers: 4</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {providers.map((p) => (
          <div key={p.provider} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white text-sm">{p.provider}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {p.health}
              </span>
            </div>

            <div className="text-xs text-slate-300 space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Risk Profile:</span>
                <span className="font-bold text-white">{p.risk}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Cost Trend:</span>
                <span className="font-bold text-indigo-300">{p.costTrend}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Active Issues:</span>
                <span className="font-bold text-amber-400">{p.activeIssues}</span>
              </div>
            </div>

            <div className="text-[10px] text-slate-500 border-t border-slate-700/50 pt-2 flex justify-between">
              <span>Region: {p.region}</span>
              <span>Telemetry: Active</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
