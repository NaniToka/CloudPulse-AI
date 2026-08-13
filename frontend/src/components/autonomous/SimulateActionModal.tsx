import React, { useState } from 'react';
import { ActionDefinition, SimulationResult } from '../../types/autonomous';
import { Play, X, CheckCircle, AlertCircle, Cpu, ShieldCheck } from 'lucide-react';

interface SimulateActionModalProps {
  action: ActionDefinition | null;
  onClose: () => void;
  onSimulateSubmit: (payload: {
    action_type: string;
    affected_resource: string;
    provider: string;
    environment: string;
    execution_mode: string;
  }) => Promise<SimulationResult>;
}

export const SimulateActionModal: React.FC<SimulateActionModalProps> = ({
  action,
  onClose,
  onSimulateSubmit,
}) => {
  const [resource, setResource] = useState('api-service-prod-pod-4');
  const [environment, setEnvironment] = useState('production');
  const [mode, setMode] = useState('SIMULATED');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);

  if (!action) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await onSimulateSubmit({
        action_type: action.action_type,
        affected_resource: resource,
        provider: action.provider,
        environment,
        execution_mode: mode,
      });
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-xl w-full p-6 shadow-2xl relative overflow-hidden">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-emerald-500/15 border border-emerald-500/30 rounded-lg text-emerald-400">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Safe Action Simulator</h3>
            <p className="text-xs text-slate-400">
              Simulate <strong className="text-emerald-400">{action.action_type}</strong> without modifying real infrastructure.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Target Resource Name</label>
            <input
              type="text"
              value={resource}
              onChange={(e) => setResource(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Target Environment</label>
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="production">production</option>
                <option value="staging">staging</option>
                <option value="development">development</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Execution Mode</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-semibold text-emerald-400"
              >
                <option value="SIMULATED">SIMULATED (Local Engine)</option>
                <option value="DRY_RUN">DRY_RUN (Provider Validation)</option>
              </select>
            </div>
          </div>

          <div className="p-3 bg-slate-800/60 border border-slate-700 rounded-lg text-xs space-y-1">
            <div className="text-slate-300 font-semibold">Action Specifications:</div>
            <div className="text-slate-400">Risk Level: <span className="text-emerald-400 font-bold">{action.risk_level}</span></div>
            <div className="text-slate-400">Provider: <span className="text-white font-medium">{action.provider}</span></div>
            <div className="text-slate-400">Description: {action.description}</div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/40"
          >
            {loading ? (
              <span>Running Simulation Pipeline...</span>
            ) : (
              <>
                <Play className="w-4 h-4" /> Run Deterministic Simulation
              </>
            )}
          </button>
        </form>

        {result && (
          <div className="mt-5 p-4 rounded-lg bg-emerald-950/50 border border-emerald-500/40 text-emerald-200 text-xs space-y-2">
            <div className="flex items-center gap-2 font-bold text-sm text-emerald-400">
              <CheckCircle className="w-5 h-5" /> Simulation Result: {result.simulation_result}
            </div>
            <p className="text-slate-300 leading-relaxed">{result.message}</p>
            <div className="font-mono text-[11px] bg-slate-950/60 p-2 rounded border border-emerald-900 text-slate-300">
              Preconditions: {JSON.stringify(result.preconditions.status)} | Verified: {JSON.stringify(result.simulated_verification.verified)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
