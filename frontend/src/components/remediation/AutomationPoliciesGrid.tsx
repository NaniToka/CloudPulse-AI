import React from 'react';
import { RemediationPolicy } from '../../types/remediation';
import { ShieldCheck, ToggleLeft, ToggleRight, Zap } from 'lucide-react';

interface AutomationPoliciesGridProps {
  policies: RemediationPolicy[];
  onTogglePolicy?: (policyId: string, currentEnabled: boolean) => Promise<void>;
}

export const AutomationPoliciesGrid: React.FC<AutomationPoliciesGridProps> = ({
  policies,
  onTogglePolicy,
}) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Automation & Self-Healing Policies</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{policies.length} Active Policies</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {policies.map((p) => (
          <div key={p.id} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white text-sm">{p.name}</span>
              <span
                className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold border ${
                  p.is_enabled
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : 'bg-slate-700 text-slate-400 border-slate-600'
                }`}
              >
                {p.is_enabled ? 'ENABLED' : 'DISABLED'}
              </span>
            </div>

            <div className="text-xs text-slate-300 space-y-1 font-mono">
              <div className="flex justify-between">
                <span className="text-slate-400">Trigger Signal:</span>
                <span className="text-indigo-300">{p.trigger_signal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Action Type:</span>
                <span className="text-white">{p.action_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Risk Level:</span>
                <span className="text-amber-400">{p.risk_level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Cooldown Window:</span>
                <span className="text-slate-300">{p.cooldown_minutes} minutes</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
