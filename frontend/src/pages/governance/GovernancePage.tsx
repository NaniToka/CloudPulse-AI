import React, { useEffect, useState } from "react";
import { ShieldCheck, RefreshCw, Sparkles, Info, Play } from "lucide-react";
import { governanceService } from "@/services/governanceService";
import type {
  GovernanceOverviewResponse,
  GovernancePolicyItem,
  ComplianceFrameworkItem,
  PolicyEvaluationItem,
  GovernanceViolationItem,
  GovernanceRemediationItem,
  AuditEventItem,
  GovernanceTrendResponse,
  GovernanceAnalyzeResponse,
} from "@/types/governance";

import GovernanceOverviewCards from "@/components/governance/GovernanceOverviewCards";
import ComplianceFrameworkPanel from "@/components/governance/ComplianceFrameworkPanel";
import PolicyPostureTable from "@/components/governance/PolicyPostureTable";
import ViolationLifecycleTable from "@/components/governance/ViolationLifecycleTable";
import DomainGovernancePanels from "@/components/governance/DomainGovernancePanels";
import GovernanceRemediationPanel from "@/components/governance/GovernanceRemediationPanel";
import GovernanceAuditTrailPanel from "@/components/governance/GovernanceAuditTrailPanel";
import GovernanceTrendCard from "@/components/governance/GovernanceTrendCard";

export default function GovernancePage() {
  const [overview, setOverview] = useState<GovernanceOverviewResponse | null>(null);
  const [policies, setPolicies] = useState<GovernancePolicyItem[]>([]);
  const [frameworks, setFrameworks] = useState<ComplianceFrameworkItem[]>([]);
  const [evaluations, setEvaluations] = useState<PolicyEvaluationItem[]>([]);
  const [violations, setViolations] = useState<GovernanceViolationItem[]>([]);
  const [remediations, setRemediations] = useState<GovernanceRemediationItem[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);
  const [trends, setTrends] = useState<GovernanceTrendResponse | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<GovernanceAnalyzeResponse | null>(null);

  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [providerFilter, setProviderFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [trendDays, setTrendDays] = useState(30);

  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (cat = categoryFilter, prov = providerFilter, stat = statusFilter, sev = severityFilter, days = trendDays) => {
    try {
      setLoading(true);
      setError(null);
      const [
        ovRes,
        polRes,
        fwRes,
        evalRes,
        violRes,
        remRes,
        auditRes,
        trendRes,
      ] = await Promise.all([
        governanceService.getOverview(),
        governanceService.getPolicies({
          category: cat !== "ALL" ? cat : undefined,
          provider: prov !== "ALL" ? prov : undefined,
          severity: sev !== "ALL" ? sev : undefined,
        }),
        governanceService.getFrameworks(),
        governanceService.getEvaluations({
          provider: prov !== "ALL" ? prov : undefined,
        }),
        governanceService.getViolations({
          status: stat !== "ALL" ? stat : undefined,
          severity: sev !== "ALL" ? sev : undefined,
          provider: prov !== "ALL" ? prov : undefined,
        }),
        governanceService.getRecommendations(),
        governanceService.getAuditTrail(),
        governanceService.getTrends(days),
      ]);

      setOverview(ovRes);
      setPolicies(polRes.policies);
      setFrameworks(fwRes.frameworks);
      setEvaluations(evalRes.evaluations);
      setViolations(violRes.violations);
      setRemediations(remRes.remediations);
      setAuditEvents(auditRes.audit_events);
      setTrends(trendRes);
    } catch (err: any) {
      console.error("Failed to load governance telemetry:", err);
      setError(err?.message || "Failed to load cloud governance & compliance posture.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(categoryFilter, providerFilter, statusFilter, severityFilter, trendDays);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCategoryFilterChange = (c: string) => {
    setCategoryFilter(c);
    loadData(c, providerFilter, statusFilter, severityFilter, trendDays);
  };

  const handleProviderFilterChange = (p: string) => {
    setProviderFilter(p);
    loadData(categoryFilter, p, statusFilter, severityFilter, trendDays);
  };

  const handleStatusFilterChange = (s: string) => {
    setStatusFilter(s);
    loadData(categoryFilter, providerFilter, s, severityFilter, trendDays);
  };

  const handleSeverityFilterChange = (s: string) => {
    setSeverityFilter(s);
    loadData(categoryFilter, providerFilter, statusFilter, s, trendDays);
  };

  const handleDaysChange = (days: number) => {
    setTrendDays(days);
    loadData(categoryFilter, providerFilter, statusFilter, severityFilter, days);
  };

  const handleUpdateStatus = async (id: string, newStatus: string) => {
    try {
      await governanceService.updateViolationStatus(id, newStatus);
      await loadData();
    } catch (err: any) {
      console.error("Failed to update violation status:", err);
    }
  };

  const handleTriggerEvaluation = async () => {
    try {
      setEvaluating(true);
      await governanceService.triggerEvaluation();
      await loadData();
    } catch (err: any) {
      console.error("Evaluation sweep failed:", err);
    } finally {
      setEvaluating(false);
    }
  };

  const handleTriggerAnalysis = async () => {
    try {
      setAnalyzing(true);
      const result = await governanceService.triggerAnalysis();
      setAiAnalysis(result);
      if (result.remediation_recommendations && result.remediation_recommendations.length > 0) {
        setRemediations(result.remediation_recommendations);
      }
    } catch (err: any) {
      console.error("Governance AI analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-7 h-7 text-brand-blue" />
            <h1 className="text-2xl font-bold font-mono tracking-tight text-foreground">
              Enterprise Cloud Governance & Compliance Center
            </h1>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Automated multi-cloud policy enforcement, framework compliance (CIS, SOC 2, ISO 27001, NIST, PCI DSS), and AI posture recovery
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => loadData()}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-white/10 bg-black/40 text-xs font-mono text-foreground flex items-center gap-2 hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>

          <button
            onClick={handleTriggerEvaluation}
            disabled={evaluating}
            className="px-3.5 py-2 rounded-lg border border-indigo-500/30 bg-indigo-500/20 text-indigo-300 font-semibold text-xs font-mono flex items-center gap-2 hover:bg-indigo-500/30 transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            {evaluating ? "Evaluating..." : "Run Policy Evaluation"}
          </button>

          <button
            onClick={handleTriggerAnalysis}
            disabled={analyzing}
            className="px-4 py-2 rounded-lg bg-brand-blue text-white font-semibold text-xs font-mono flex items-center gap-2 hover:bg-brand-blue/80 transition-all disabled:opacity-50 shadow-lg shadow-brand-blue/20"
          >
            <Sparkles className="w-4 h-4" />
            {analyzing ? "Analyzing Posture..." : "Run AI Governance Analysis"}
          </button>
        </div>
      </div>

      {/* Fixture Notification Banner */}
      <div className="p-3.5 rounded-xl border border-blue-500/20 bg-blue-500/10 backdrop-blur-md flex items-center gap-3 text-xs font-mono text-blue-200">
        <Info className="w-4 h-4 text-blue-400 shrink-0" />
        <span>{overview?.data_source || "Local Governance Data — AWS/Azure/GCP/Kubernetes Fixtures"}</span>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-xs text-rose-300 font-mono">
          {error}
        </div>
      )}

      {/* AI Analysis Summary Banner */}
      {aiAnalysis && (
        <div className="p-5 rounded-xl border border-amber-500/30 bg-amber-500/10 backdrop-blur-md space-y-3 font-mono">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <h3 className="text-sm font-semibold text-foreground">Governance AI Executive Summary</h3>
            </div>
            <span className="text-[11px] text-amber-300 font-bold">Engine: {aiAnalysis.analysis_engine}</span>
          </div>

          <p className="text-xs text-slate-200 leading-relaxed">{aiAnalysis.executive_summary}</p>

          {aiAnalysis.critical_violations.length > 0 && (
            <div className="pt-2 border-t border-amber-500/20 text-xs text-rose-300 space-y-1">
              <span className="font-bold">Critical Violations Requiring Immediate Action:</span>
              <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                {aiAnalysis.critical_violations.map((cv, idx) => (
                  <li key={idx}>{cv}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* KPI Overview Cards */}
      <GovernanceOverviewCards overview={overview} />

      {/* Compliance Frameworks Panel */}
      <ComplianceFrameworkPanel frameworks={frameworks} />

      {/* Policy Rules Matrix */}
      <PolicyPostureTable
        policies={policies}
        categoryFilter={categoryFilter}
        providerFilter={providerFilter}
        onCategoryFilterChange={handleCategoryFilterChange}
        onProviderFilterChange={handleProviderFilterChange}
      />

      {/* Non-Compliant Resource Violations */}
      <ViolationLifecycleTable
        violations={violations}
        statusFilter={statusFilter}
        severityFilter={severityFilter}
        onStatusFilterChange={handleStatusFilterChange}
        onSeverityFilterChange={handleSeverityFilterChange}
        onUpdateStatus={handleUpdateStatus}
      />

      {/* Domain Governance Breakdown */}
      <DomainGovernancePanels overview={overview} />

      {/* Historical Compliance Trends */}
      <GovernanceTrendCard
        trends={trends}
        selectedDays={trendDays}
        onDaysChange={handleDaysChange}
      />

      {/* Remediation Plan */}
      <GovernanceRemediationPanel
        remediations={remediations}
        onTriggerAnalysis={handleTriggerAnalysis}
        isAnalyzing={analyzing}
      />

      {/* Audit Trail & History */}
      <GovernanceAuditTrailPanel auditEvents={auditEvents} />
    </div>
  );
}
