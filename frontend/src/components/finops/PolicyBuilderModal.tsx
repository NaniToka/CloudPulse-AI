import React, { useState } from "react";
import type { CostPolicyCreatePayload } from "@/types/finopsGovernance";
import { X, PlusCircle, ShieldAlert } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CostPolicyCreatePayload) => Promise<void>;
}

export const PolicyBuilderModal: React.FC<Props> = ({ isOpen, onClose, onSubmit }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("SPENDING");
  const [provider, setProvider] = useState("all");
  const [scope, setScope] = useState("all");
  const [metric, setMetric] = useState("monthly_spend");
  const [operator, setOperator] = useState(">");
  const [thresholdValue, setThresholdValue] = useState<number>(5000);
  const [severity, setSeverity] = useState("MEDIUM");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Policy name is required.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        name,
        description,
        category,
        provider,
        scope,
        metric,
        operator,
        threshold_value: Number(thresholdValue),
        severity,
        enabled: true,
      });
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create policy";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
              <PlusCircle className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-100">Create FinOps Cost Policy</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 transition-colors p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-xs flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Policy Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. AWS Production Compute Spend Cap"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe policy intent and enforcement rules..."
              rows={2}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="SPENDING">SPENDING</option>
                <option value="BUDGET">BUDGET</option>
                <option value="RESOURCE">RESOURCE</option>
                <option value="SERVICE">SERVICE</option>
                <option value="PROVIDER">PROVIDER</option>
                <option value="REGION">REGION</option>
                <option value="WASTE">WASTE</option>
                <option value="ANOMALY">ANOMALY</option>
                <option value="FORECAST">FORECAST</option>
                <option value="KUBERNETES">KUBERNETES</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Severity</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="INFO">INFO</option>
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Cloud Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="all">Multi-Cloud (All)</option>
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">GCP</option>
                <option value="kubernetes">Kubernetes</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Environment Scope</label>
              <select
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="all">All Environments</option>
                <option value="production">Production</option>
                <option value="staging">Staging</option>
                <option value="development">Development</option>
              </select>
            </div>
          </div>

          <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg space-y-3">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block">Rule Condition Engine</span>
            
            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-1">
                <label className="block text-[11px] font-medium text-slate-400 mb-1">Metric Target</label>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
                >
                  <option value="monthly_spend">Monthly Spend ($)</option>
                  <option value="daily_spend">Daily Spend ($)</option>
                  <option value="resource_cost">Single Resource Cost ($)</option>
                  <option value="waste_cost">Idle Waste Cost ($)</option>
                  <option value="anomaly_score">Anomaly Score</option>
                  <option value="budget_utilization">Budget Utilization (%)</option>
                </select>
              </div>

              <div className="col-span-1">
                <label className="block text-[11px] font-medium text-slate-400 mb-1">Operator</label>
                <select
                  value={operator}
                  onChange={(e) => setOperator(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
                >
                  <option value=">">&gt; (Greater Than)</option>
                  <option value=">=">&gt;= (Greater or Equal)</option>
                  <option value="<">&lt; (Less Than)</option>
                  <option value="<=">&lt;= (Less or Equal)</option>
                  <option value="==">== (Equal To)</option>
                  <option value="!=">!= (Not Equal)</option>
                </select>
              </div>

              <div className="col-span-1">
                <label className="block text-[11px] font-medium text-slate-400 mb-1">Threshold Limit</label>
                <input
                  type="number"
                  step="any"
                  value={thresholdValue}
                  onChange={(e) => setThresholdValue(parseFloat(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
                  required
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition-colors disabled:opacity-50"
            >
              {loading ? "Creating Policy..." : "Create Policy"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
