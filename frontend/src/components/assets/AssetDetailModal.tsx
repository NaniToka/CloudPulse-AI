import React from 'react';
import {
  X,
  Server,
  DollarSign,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Cpu,
  Activity,
  HardDrive,
  GitCommit,
  CheckCircle2,
  FileText,
} from 'lucide-react';
import { AssetDetailResponse } from '../../types/assets';

interface AssetDetailModalProps {
  detail?: AssetDetailResponse | null;
  onClose: () => void;
}

export const AssetDetailModal: React.FC<AssetDetailModalProps> = ({ detail, onClose }) => {
  if (!detail) return null;

  const { resource, relationships, security_findings, governance_violations, finops_optimization, related_incidents, telemetry_summary } = detail;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-slate-900/95 backdrop-blur z-10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
              <Server className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">{resource.name}</h2>
              <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                <span>{resource.provider}</span>
                <span>•</span>
                <span>{resource.service}</span>
                <span>•</span>
                <span>{resource.region}</span>
                <span>•</span>
                <span className="capitalize">{resource.environment}</span>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Health Status</span>
              <div className="text-lg font-bold text-emerald-400 mt-1 capitalize">{resource.status}</div>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Monthly Burn</span>
              <div className="text-lg font-bold text-slate-100 mt-1">${resource.monthly_cost}</div>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Security Risk Score</span>
              <div className="text-lg font-bold text-amber-400 mt-1">{resource.risk_score} / 100</div>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Governance Compliance</span>
              <div className="text-lg font-bold text-slate-100 mt-1">{resource.governance_compliance_status}</div>
            </div>
          </div>

          {/* Telemetry Metrics */}
          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-400" />
              Resource Telemetry & Utilization Metrics
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-indigo-400" /> CPU Utilization
                </div>
                <div className="text-xl font-bold text-slate-100 mt-2">{telemetry_summary.cpu_percent ?? 'N/A'}%</div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400 flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-sky-400" /> Memory Utilization
                </div>
                <div className="text-xl font-bold text-slate-100 mt-2">{telemetry_summary.memory_percent ?? 'N/A'}%</div>
              </div>
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400 flex items-center gap-1.5">
                  <HardDrive className="w-4 h-4 text-slate-400" /> Storage Utilization
                </div>
                <div className="text-xl font-bold text-slate-100 mt-2">{telemetry_summary.disk_percent ?? 'N/A'}%</div>
              </div>
            </div>
          </div>

          {/* FinOps Optimization */}
          {finops_optimization && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 p-5 rounded-xl">
              <h3 className="text-sm font-bold text-emerald-400 mb-2 flex items-center gap-2">
                <DollarSign className="w-4 h-4" /> FinOps Cost Intelligence & Right-Sizing
              </h3>
              <p className="text-xs text-slate-300">
                Recommendation: Right-size from current configuration to{' '}
                <span className="font-bold text-emerald-300">{finops_optimization.recommended_instance_type}</span>.
                Estimated monthly savings:{' '}
                <span className="font-bold text-emerald-300">${finops_optimization.potential_monthly_savings}</span>.
              </p>
            </div>
          )}

          {/* Security & Governance Findings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" /> Security Vulnerability Findings ({security_findings.length})
              </h3>
              {security_findings.length === 0 ? (
                <p className="text-xs text-slate-500">No active security vulnerabilities detected.</p>
              ) : (
                security_findings.map((sf, idx) => (
                  <div key={idx} className="p-3 bg-slate-900 rounded-lg border border-slate-800 mb-2">
                    <div className="text-xs font-semibold text-slate-200">{sf.title}</div>
                    <div className="text-[11px] text-amber-400 mt-1">Severity: {sf.severity} • {sf.cve_id}</div>
                  </div>
                ))
              )}
            </div>

            <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-sky-400" /> Governance Compliance Policies ({governance_violations.length})
              </h3>
              {governance_violations.length === 0 ? (
                <p className="text-xs text-slate-500">Resource fully compliant with organization policies.</p>
              ) : (
                governance_violations.map((gv, idx) => (
                  <div key={idx} className="p-3 bg-slate-900 rounded-lg border border-slate-800 mb-2">
                    <div className="text-xs font-semibold text-slate-200">{gv.policy_name}</div>
                    <div className="text-[11px] text-slate-400 mt-1">{gv.recommendation}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Relationship Graph */}
          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
              <GitCommit className="w-4 h-4 text-indigo-400" /> Dependency Topology Relationships ({relationships.length})
            </h3>
            {relationships.map((rel) => (
              <div key={rel.id} className="p-3 bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-200">{rel.source_name}</span>
                <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">{rel.relationship_type}</span>
                <span className="font-semibold text-slate-200">{rel.target_name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-800 bg-slate-900 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition shadow-lg shadow-indigo-600/20"
          >
            Close Asset Intelligence
          </button>
        </div>
      </div>
    </div>
  );
};
