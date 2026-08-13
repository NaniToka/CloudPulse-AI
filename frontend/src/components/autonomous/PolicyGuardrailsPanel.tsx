import React from 'react';
import { AutonomyPolicy } from '../../types/autonomous';
import { ShieldCheck, Lock, Sliders, AlertTriangle } from 'lucide-react';

interface PolicyGuardrailsPanelProps {
  policy: AutonomyPolicy | null;
  onUpdate: (policy: Partial<AutonomyPolicy>) => void;
}

export const PolicyGuardrailsPanel: React.FC<PolicyGuardrailsPanelProps> = ({ policy, onUpdate }) => {
  if (!policy) return null;

  const handleMaxRiskChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onUpdate({ max_autonomous_risk: e.target.value as any });
  };

  const handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onUpdate({ default_execution_mode: e.target.value as any });
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Policy Guardrails & Safety Settings</h3>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          Guardrails Active
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg">
          <label className="text-xs font-semibold text-slate-300 block mb-1.5">
            Max Autonomous Risk Threshold
          </label>
          <select
            value={policy.max_autonomous_risk}
            onChange={handleMaxRiskChange}
            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="LOW">LOW Risk Only</option>
            <option value="MEDIUM">MEDIUM Risk & Below</option>
            <option value="HIGH">HIGH Risk (Require Manual Check)</option>
            <option value="CRITICAL">CRITICAL (Require Multi-Approver)</option>
          </select>
          <p className="text-[11px] text-slate-400 mt-2">
            Actions above this risk level unconditionally require human authorization.
          </p>
        </div>

        <div className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg">
          <label className="text-xs font-semibold text-slate-300 block mb-1.5">
            Default Execution Mode
          </label>
          <select
            value={policy.default_execution_mode}
            onChange={handleModeChange}
            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="SIMULATED">SIMULATED (Deterministic Engine)</option>
            <option value="DRY_RUN">DRY_RUN (API Validation Only)</option>
            <option value="LIVE">LIVE (Cloud Credentials Required)</option>
          </select>
          <p className="text-[11px] text-slate-400 mt-2">
            Default execution target. Defaults to SIMULATED if credentials missing.
          </p>
        </div>

        <div className="p-3.5 bg-slate-800/50 border border-slate-700/60 rounded-lg">
          <label className="text-xs font-semibold text-slate-300 block mb-1.5">
            Allowed Cloud Providers
          </label>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {(policy.allowed_providers || ['AWS', 'Azure', 'GCP', 'Kubernetes']).map((prov) => (
              <span
                key={prov}
                className="px-2 py-1 rounded bg-slate-900 text-slate-200 border border-slate-700 text-xs font-semibold"
              >
                {prov}
              </span>
            ))}
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Configured target cloud ecosystems enabled for self-healing.
          </p>
        </div>
      </div>
    </div>
  );
};
