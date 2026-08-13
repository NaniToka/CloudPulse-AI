import React, { useEffect, useState, useCallback } from "react";
import { finopsGovernanceService } from "@/services/finopsGovernanceService";
import type {
  CostPolicy,
  CostViolation,
  FinOpsAuditLog,
  GovernanceOverviewResponse,
  GovernanceScoreResponse,
  PolicyException,
  RemediationAction,
  CostPolicyCreatePayload,
  PolicyExceptionCreatePayload,
  RemediationRequestPayload,
} from "@/types/finopsGovernance";
import { GovernanceScoreCard } from "@/components/finops/GovernanceScoreCard";
import { PolicyBuilderModal } from "@/components/finops/PolicyBuilderModal";
import { PolicyListTable } from "@/components/finops/PolicyListTable";
import { ViolationListPanel } from "@/components/finops/ViolationListPanel";
import { PolicyExceptionModal } from "@/components/finops/PolicyExceptionModal";
import { RemediationQueuePanel } from "@/components/finops/RemediationQueuePanel";
import { GovernanceAuditLogTable } from "@/components/finops/GovernanceAuditLogTable";
import { ShieldCheck, AlertCircle, RefreshCw, ShieldAlert, FileText } from "lucide-react";

export const FinOpsGovernancePage: React.FC = () => {
  const [score, setScore] = useState<GovernanceScoreResponse | null>(null);
  const [overview, setOverview] = useState<GovernanceOverviewResponse | null>(null);
  const [policies, setPolicies] = useState<CostPolicy[]>([]);
  const [violations, setViolations] = useState<CostViolation[]>([]);
  const [exceptions, setExceptions] = useState<PolicyException[]>([]);
  const [remediations, setRemediations] = useState<RemediationAction[]>([]);
  const [auditLogs, setAuditLogs] = useState<FinOpsAuditLog[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [isBuilderOpen, setIsBuilderOpen] = useState<boolean>(false);
  const [isExceptionOpen, setIsExceptionOpen] = useState<boolean>(false);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [scoreRes, overviewRes, polRes, violRes, excRes, remRes, auditRes] = await Promise.all([
        finopsGovernanceService.getScore(),
        finopsGovernanceService.getOverview(),
        finopsGovernanceService.getPolicies(),
        finopsGovernanceService.getViolations(),
        finopsGovernanceService.getExceptions(),
        finopsGovernanceService.getRemediations(),
        finopsGovernanceService.getAuditTrail(),
      ]);

      setScore(scoreRes);
      setOverview(overviewRes);
      setPolicies(polRes.policies);
      setViolations(violRes.violations);
      setExceptions(excRes.exceptions);
      setRemediations(remRes.remediations);
      setAuditLogs(auditRes.audit_logs);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load FinOps Governance data";
      setError(msg);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const handleCreatePolicy = async (payload: CostPolicyCreatePayload) => {
    await finopsGovernanceService.createPolicy(payload);
    fetchData();
  };

  const handleTogglePolicyStatus = async (id: string, currentEnabled: boolean) => {
    await finopsGovernanceService.togglePolicyStatus(id, !currentEnabled);
    fetchData();
  };

  const handleEvaluatePolicy = async (id: string) => {
    await finopsGovernanceService.evaluatePolicy(id);
    fetchData();
  };

  const handleDeletePolicy = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this cost policy?")) {
      await finopsGovernanceService.deletePolicy(id);
      fetchData();
    }
  };

  const handleUpdateViolationStatus = async (id: string, newStatus: string) => {
    await finopsGovernanceService.updateViolationStatus(id, newStatus);
    fetchData();
  };

  const handleCreateException = async (payload: PolicyExceptionCreatePayload) => {
    await finopsGovernanceService.createException(payload);
    fetchData();
  };

  const handleRequestRemediationFromViolation = async (viol: CostViolation) => {
    const payload: RemediationRequestPayload = {
      violation_id: viol.id,
      action_type: "stop_idle_compute",
      resource_name: viol.resource_name,
      provider: viol.provider,
      estimated_savings: viol.difference > 0 ? viol.difference : 1200,
      risk_level: "low",
      execution_mode: "DRY_RUN",
    };
    await finopsGovernanceService.requestRemediation(payload);
    fetchData();
  };

  const handleApproveRemediation = async (id: string, status: string) => {
    await finopsGovernanceService.approveRemediation(id, status);
    fetchData();
  };

  const handleExecuteRemediation = async (id: string, mode: string) => {
    await finopsGovernanceService.executeRemediation(id, mode);
    fetchData();
  };

  const handleRollbackRemediation = async (id: string) => {
    await finopsGovernanceService.rollbackRemediation(id);
    fetchData();
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto text-slate-100">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black tracking-tight text-white">
              FinOps Governance & Cost Control Center
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold tracking-wider uppercase">
              ENFORCEMENT ENGINE ACTIVE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Multi-cloud cost policy guardrails, violation tracking, exception management, and controlled remediation workflows.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsExceptionOpen(true)}
            className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-1.5"
          >
            <FileText className="w-4 h-4 text-amber-400" /> Exception Request
          </button>

          <button
            onClick={() => setIsBuilderOpen(true)}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-500/20"
          >
            + Build Policy
          </button>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-2 text-slate-400 hover:text-slate-200 bg-slate-800 border border-slate-700 rounded-lg transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Top Metrics Cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Active Policies</span>
            <div className="text-2xl font-extrabold text-slate-100">{overview.active_policies} <span className="text-xs text-slate-500 font-normal">/ {overview.total_policies}</span></div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Open Violations</span>
            <div className="text-2xl font-extrabold text-rose-400">{overview.open_violations} <span className="text-xs text-rose-500 font-normal">({overview.critical_violations} Critical)</span></div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Active Exceptions</span>
            <div className="text-2xl font-extrabold text-amber-400">{overview.active_exceptions}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Remediation Savings</span>
            <div className="text-2xl font-extrabold text-emerald-400">${overview.total_potential_savings.toLocaleString()}</div>
          </div>
        </div>
      )}

      {/* Governance Score Section */}
      <GovernanceScoreCard score={score} loading={loading} />

      {/* Main Grid: Policy Table + Violation Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PolicyListTable
          policies={policies}
          loading={loading}
          onToggleStatus={handleTogglePolicyStatus}
          onEvaluate={handleEvaluatePolicy}
          onDelete={handleDeletePolicy}
          onOpenCreate={() => setIsBuilderOpen(true)}
        />

        <ViolationListPanel
          violations={violations}
          loading={loading}
          onUpdateStatus={handleUpdateViolationStatus}
          onRequestRemediation={handleRequestRemediationFromViolation}
        />
      </div>

      {/* Remediation Queue Section */}
      <RemediationQueuePanel
        remediations={remediations}
        loading={loading}
        onApprove={handleApproveRemediation}
        onExecute={handleExecuteRemediation}
        onRollback={handleRollbackRemediation}
      />

      {/* Audit Log Stream */}
      <GovernanceAuditLogTable logs={auditLogs} loading={loading} />

      {/* Modals */}
      <PolicyBuilderModal
        isOpen={isBuilderOpen}
        onClose={() => setIsBuilderOpen(false)}
        onSubmit={handleCreatePolicy}
      />

      <PolicyExceptionModal
        isOpen={isExceptionOpen}
        policies={policies}
        onClose={() => setIsExceptionOpen(false)}
        onSubmit={handleCreateException}
      />
    </div>
  );
};
