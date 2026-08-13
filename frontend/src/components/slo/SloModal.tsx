import React, { useState } from 'react';
import { SloObjective } from '../../types/slo';
import { X, Target, Plus, Check } from 'lucide-react';

interface SloModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: Partial<SloObjective>) => Promise<void>;
  editingSlo?: SloObjective | null;
}

export const SloModal: React.FC<SloModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  editingSlo,
}) => {
  const [service, setService] = useState(editingSlo?.service || 'payment-service');
  const [name, setName] = useState(editingSlo?.name || 'Payment API Availability Target');
  const [description, setDescription] = useState(editingSlo?.description || '99.9% availability target over 30d rolling window');
  const [indicatorType, setIndicatorType] = useState(editingSlo?.indicator_type || 'availability');
  const [target, setTarget] = useState(editingSlo?.target || 99.9);
  const [thresholdMs, setThresholdMs] = useState(editingSlo?.target_threshold_ms || 500);
  const [window, setWindow] = useState(editingSlo?.window || '30d');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit({
        service,
        name,
        description,
        indicator_type: indicatorType,
        target: Number(target),
        target_threshold_ms: Number(thresholdMs),
        window,
        enabled: true,
      });
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-indigo-500/15 border border-indigo-500/30 rounded-lg text-indigo-400">
            <Target className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              {editingSlo ? 'Edit Service Level Objective' : 'Create Service Level Objective (SLO)'}
            </h3>
            <p className="text-xs text-slate-400">Define reliability targets and error budget thresholds.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Target Service</label>
            <input
              type="text"
              value={service}
              onChange={(e) => setService(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Objective Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Indicator Type</label>
              <select
                value={indicatorType}
                onChange={(e) => setIndicatorType(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="availability">availability</option>
                <option value="latency">latency</option>
                <option value="error_rate">error_rate</option>
                <option value="throughput">throughput</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Target Percent (%)</label>
              <input
                type="number"
                step="0.01"
                value={target}
                onChange={(e) => setTarget(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono font-bold text-emerald-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Latency Threshold (ms)</label>
              <input
                type="number"
                value={thresholdMs}
                onChange={(e) => setThresholdMs(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Time Window</label>
              <select
                value={window}
                onChange={(e) => setWindow(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="30d">30 Days (Rolling)</option>
                <option value="7d">7 Days (Rolling)</option>
                <option value="24h">24 Hours</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-indigo-950/40"
          >
            {loading ? 'Saving Objective...' : editingSlo ? 'Update Objective' : 'Create Objective'}
          </button>
        </form>
      </div>
    </div>
  );
};
