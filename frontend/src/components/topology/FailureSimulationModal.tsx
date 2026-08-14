import React, { useState } from 'react';
import { X, Play, AlertTriangle, ShieldCheck, CheckCircle2, ArrowRight } from 'lucide-react';
import { FailureSimulationResponse, TopologyNodeItem } from '../../types/topology';

interface FailureSimulationModalProps {
  nodes: TopologyNodeItem[];
  simulationResult?: FailureSimulationResponse | null;
  onSimulate: (nodeId: string, failureType: string) => void;
  onClose: () => void;
  isLoading: boolean;
}

export const FailureSimulationModal: React.FC<FailureSimulationModalProps> = ({
  nodes,
  simulationResult,
  onSimulate,
  onClose,
  isLoading,
}) => {
  const [selectedNodeId, setSelectedNodeId] = useState(nodes[0]?.id || '');
  const [failureType, setFailureType] = useState('TOTAL_OUTAGE');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedNodeId) {
      onSimulate(selectedNodeId, failureType);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-rose-500/30 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-slate-900/95 backdrop-blur z-10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
              <Play className="w-6 h-6 fill-current" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                Simulate Infrastructure Failure
                <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 uppercase">
                  Simulation Only
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Model topological blast radius and cascading failure propagation without modifying production infrastructure.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Select Node / Service to Fail
                </label>
                <select
                  value={selectedNodeId}
                  onChange={(e) => setSelectedNodeId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                >
                  {nodes.map((n) => (
                    <option key={n.id} value={n.id}>
                      {n.name} ({n.provider} • {n.type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Failure Scenario Type
                </label>
                <select
                  value={failureType}
                  onChange={(e) => setFailureType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
                >
                  <option value="TOTAL_OUTAGE">Total Instance Outage (CRITICAL)</option>
                  <option value="LATENCY_SPIKE">Extreme Network Latency Spike (+500ms)</option>
                  <option value="NETWORK_PARTITION">VPC Network Partition</option>
                  <option value="DISK_SATURATION">Storage / Disk Exhaustion (100%)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm rounded-lg shadow-lg shadow-rose-600/20 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-current" />
              )}
              Run Topological Failure Simulation
            </button>
          </form>

          {/* Results Output */}
          {simulationResult && (
            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                  Simulation Outcome
                </span>
                <span className="text-xs text-slate-400">
                  Target: {simulationResult.target_node_name}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[11px] text-slate-400">Blast Radius Severity</div>
                  <div className="text-sm font-bold text-rose-400 mt-1">
                    {simulationResult.blast_radius.severity}
                  </div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[11px] text-slate-400">Affected Nodes</div>
                  <div className="text-sm font-bold text-slate-100 mt-1">
                    {simulationResult.blast_radius.affected_node_count}
                  </div>
                </div>
                <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                  <div className="text-[11px] text-slate-400">SPOF Triggered</div>
                  <div className="text-sm font-bold text-amber-400 mt-1">
                    {simulationResult.spof_detected ? 'YES' : 'NO'}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-300 mb-2">Recommended Mitigation Steps</h4>
                <ul className="space-y-1 text-xs text-slate-400 list-disc list-inside">
                  {simulationResult.mitigation_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-slate-800 bg-slate-900 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg transition"
          >
            Close Simulation
          </button>
        </div>
      </div>
    </div>
  );
};
