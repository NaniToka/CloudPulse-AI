import React, { useEffect, useState } from 'react';
import {
  RemediationAnalyzeResult,
  RemediationAuditItem,
  RemediationExecution,
  RemediationOverview,
  RemediationPlan,
  RemediationPolicy,
} from '../../types/remediation';
import { remediationService, RemediationFilterParams } from '../../services/remediationService';
import { RemediationHeader } from '../../components/remediation/RemediationHeader';
import { RemediationOverviewMetrics } from '../../components/remediation/RemediationOverviewMetrics';
import { AiRecommendationsPanel } from '../../components/remediation/AiRecommendationsPanel';
import { PendingApprovalsTable } from '../../components/remediation/PendingApprovalsTable';
import { ActiveExecutionsPanel } from '../../components/remediation/ActiveExecutionsPanel';
import { RemediationHistoryTable } from '../../components/remediation/RemediationHistoryTable';
import { RollbackCenterPanel } from '../../components/remediation/RollbackCenterPanel';
import { AutomationPoliciesGrid } from '../../components/remediation/AutomationPoliciesGrid';
import { RemediationEffectivenessCard } from '../../components/remediation/RemediationEffectivenessCard';
import { AuditTrailTable } from '../../components/remediation/AuditTrailTable';
import { RemediationDetailModal } from '../../components/remediation/RemediationDetailModal';
import { AlertCircle, RefreshCw, Bot } from 'lucide-react';

export const AIOpsActionCenterPage: React.FC = () => {
  const [overview, setOverview] = useState<RemediationOverview | null>(null);
  const [plans, setPlans] = useState<RemediationPlan[]>([]);
  const [executions, setExecutions] = useState<RemediationExecution[]>([]);
  const [policies, setPolicies] = useState<RemediationPolicy[]>([]);
  const [auditLogs, setAuditLogs] = useState<RemediationAuditItem[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<RemediationAnalyzeResult | null>(null);

  const [selectedPlan, setSelectedPlan] = useState<RemediationPlan | null>(null);
  const [filters, setFilters] = useState<RemediationFilterParams>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRemediationData = async (currentFilters?: RemediationFilterParams) => {
    setLoading(true);
    setError(null);
    try {
      const activeFilters = currentFilters || filters;
      const [ovData, plansData, execsData, polData, auditData] = await Promise.all([
        remediationService.getOverview(),
        remediationService.getActions(activeFilters),
        remediationService.getExecutions(),
        remediationService.getPolicies(),
        remediationService.getAuditLogs(),
      ]);

      setOverview(ovData);
      setPlans(plansData);
      setExecutions(execsData);
      setPolicies(polData);
      setAuditLogs(auditData);
    } catch (err: any) {
      console.error('Failed to fetch remediation data:', err);
      setError(err?.message || 'Failed to load AIOps Action Center data.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await remediationService.analyzeRemediation();
      setAiAnalysis(res);
    } catch (err: any) {
      console.error('Failed to run AI remediation analysis:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApprove = async (planId: string, comments?: string) => {
    await remediationService.approveAction(planId, comments);
    await fetchRemediationData();
  };

  const handleReject = async (planId: string, reason: string) => {
    await remediationService.rejectAction(planId, reason);
    await fetchRemediationData();
  };

  const handleDryRun = async (planId: string) => {
    await remediationService.dryRunAction(planId);
    await fetchRemediationData();
  };

  const handleExecute = async (planId: string) => {
    await remediationService.executeAction(planId, 'SIMULATION');
    await fetchRemediationData();
  };

  const handleRollback = async (executionId: string) => {
    await remediationService.rollbackAction(executionId);
    await fetchRemediationData();
  };

  useEffect(() => {
    fetchRemediationData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilterChange = (newFilters: RemediationFilterParams) => {
    setFilters(newFilters);
    fetchRemediationData(newFilters);
  };

  if (loading && !overview) {
    return (
      <div className="p-12 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-400" />
        <p className="text-sm font-semibold">Loading AIOps Action Center & Automated Remediation Platform...</p>
      </div>
    );
  }

  if (error && !overview) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-rose-950/40 border border-rose-500/40 rounded-xl text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
        <div>
          <h3 className="text-lg font-bold text-white">Failed to Load AIOps Action Center</h3>
          <p className="text-xs text-rose-200 mt-1">{error}</p>
        </div>
        <button
          onClick={() => fetchRemediationData()}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-lg transition-colors"
        >
          Retry Load
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Header & Filters */}
      <RemediationHeader
        filters={filters}
        onFilterChange={handleFilterChange}
        onRefresh={() => fetchRemediationData()}
        onAnalyze={handleAnalyze}
        loading={loading}
        analyzing={analyzing}
      />

      {/* Overview Metrics */}
      <RemediationOverviewMetrics overview={overview} />

      {/* AI Recommendations Panel */}
      <AiRecommendationsPanel analysis={aiAnalysis} />

      {/* Pending Approvals Table */}
      <PendingApprovalsTable
        plans={plans}
        onApprove={handleApprove}
        onReject={handleReject}
        onDryRun={handleDryRun}
        onSelectPlan={(p) => setSelectedPlan(p)}
      />

      {/* Active Executions Stream */}
      <ActiveExecutionsPanel executions={executions} />

      {/* Remediation Action History */}
      <RemediationHistoryTable
        plans={plans}
        onSelectPlan={(p) => setSelectedPlan(p)}
        onExecute={handleExecute}
      />

      {/* Rollback Center & Automation Policies Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RollbackCenterPanel executions={executions} onRollback={handleRollback} />
        <AutomationPoliciesGrid policies={policies} />
      </div>

      {/* Remediation Effectiveness */}
      <RemediationEffectivenessCard />

      {/* Immutable Security Audit Trail */}
      <AuditTrailTable auditLogs={auditLogs} />

      {/* Interactive Detail View Modal */}
      {selectedPlan && (
        <RemediationDetailModal
          plan={selectedPlan}
          onClose={() => setSelectedPlan(null)}
          onExecute={handleExecute}
          onDryRun={handleDryRun}
        />
      )}
    </div>
  );
};
