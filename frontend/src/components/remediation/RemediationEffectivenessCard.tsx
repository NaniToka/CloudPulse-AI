import React from 'react';
import { RemediationEffectivenessItem } from '../../types/remediation';
import { TrendingUp, CheckCircle2, AlertCircle } from 'lucide-react';

interface RemediationEffectivenessCardProps {
  effectivenessList?: RemediationEffectivenessItem[];
}

export const RemediationEffectivenessCard: React.FC<RemediationEffectivenessCardProps> = ({
  effectivenessList,
}) => {
  const defaults: RemediationEffectivenessItem[] = effectivenessList || [
    {
      plan_id: 'sample-1',
      service_name: 'payment-service',
      action_type: 'SERVICE_RESTART',
      pre_action_metric: 7.2,
      post_action_metric: 1.8,
      improvement_pct: 75.0,
      verification_status: 'IMPROVED',
      verification_window_minutes: 15,
    },
    {
      plan_id: 'sample-2',
      service_name: 'order-processor',
      action_type: 'SCALE_UP',
      pre_action_metric: 88.0,
      post_action_metric: 42.0,
      improvement_pct: 52.27,
      verification_status: 'IMPROVED',
      verification_window_minutes: 15,
    },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">Post-Remediation Telemetry Effectiveness & Resolution %</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">15-Minute Verification Windows</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {defaults.map((eff, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white text-sm">{eff.service_name}</span>
              <span
                className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold ${
                  eff.verification_status === 'IMPROVED'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}
              >
                {eff.verification_status}
              </span>
            </div>

            <div className="text-xs text-slate-300 space-y-1.5 font-mono">
              <div className="flex justify-between">
                <span className="text-slate-400">Action Executed:</span>
                <span className="text-indigo-300 font-bold">{eff.action_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Pre-Action Error / Saturation Metric:</span>
                <span className="text-rose-400 font-bold">{eff.pre_action_metric}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Post-Action Telemetry Metric:</span>
                <span className="text-emerald-400 font-bold">{eff.post_action_metric}%</span>
              </div>
              <div className="flex justify-between border-t border-slate-700/50 pt-1.5 font-bold">
                <span className="text-slate-300">Measured Improvement:</span>
                <span className="text-emerald-300 text-sm">+{eff.improvement_pct}% Improvement</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
