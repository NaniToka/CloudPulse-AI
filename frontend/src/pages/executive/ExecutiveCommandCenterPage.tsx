import React, { useEffect, useState } from 'react';
import { Download, RefreshCw, Filter, ShieldCheck, Cpu, LayoutDashboard, FileText, AlertCircle } from 'lucide-react';
import { executiveService } from '../../services/executiveService';
import { ExecutiveOverviewResponse } from '../../types/executive';
import { ExecutiveHealthGauge } from '../../components/executive/ExecutiveHealthGauge';
import { ExecutiveSummaryCard } from '../../components/executive/ExecutiveSummaryCard';
import { KeyMetricsGrid } from '../../components/executive/KeyMetricsGrid';
import { TopPrioritiesQueue } from '../../components/executive/TopPrioritiesQueue';
import { ProviderHealthGrid } from '../../components/executive/ProviderHealthGrid';
import { OperationalTrendsChart } from '../../components/executive/OperationalTrendsChart';
import { ExecutiveServiceHealthMap } from '../../components/executive/ExecutiveServiceHealthMap';
import { CloudRiskMatrixTable } from '../../components/executive/CloudRiskMatrixTable';
import { WhatChangedTable } from '../../components/executive/WhatChangedTable';
import { ExecutiveTimelineFeed } from '../../components/executive/ExecutiveTimelineFeed';
import { RecommendedActionsList } from '../../components/executive/RecommendedActionsList';

export const ExecutiveCommandCenterPage: React.FC = () => {
  const [data, setData] = useState<ExecutiveOverviewResponse | null>(null);
  const [services, setServices] = useState<any[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [selectedProvider, setSelectedProvider] = useState<string>('ALL');
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const [overviewData, servicesRes, timelineRes, recsRes] = await Promise.all([
        executiveService.getOverview(),
        executiveService.getServices(),
        executiveService.getTimeline(),
        executiveService.getRecommendations(),
      ]);
      setData(overviewData);
      setServices(servicesRes.services);
      setTimelineEvents(timelineRes.events);
      setRecommendations(recsRes.recommendations);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load Executive Overview data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const handleExportPdf = async () => {
    try {
      const blob = await executiveService.exportPdf();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Executive_Cloud_Operations_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to export PDF report: ' + (err.message || err));
    }
  };

  const handleExportCsv = async () => {
    try {
      const blob = await executiveService.exportCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Executive_Cloud_Metrics_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to export CSV: ' + (err.message || err));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 p-8 flex flex-col items-center justify-center">
        <RefreshCw className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
        <h2 className="text-xl font-bold tracking-tight">Aggregating Executive Operations Intelligence...</h2>
        <p className="text-sm text-slate-400 mt-1">Collecting telemetry across Reliability, Security, FinOps, Governance, and Capacity</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 p-8 flex flex-col items-center justify-center">
        <AlertCircle className="w-12 h-12 text-rose-500 mb-4" />
        <h2 className="text-xl font-bold tracking-tight">Failed to Load Executive Command Center</h2>
        <p className="text-sm text-rose-400 mt-1 max-w-md text-center">{error}</p>
        <button
          id="retry-btn"
          onClick={fetchOverview}
          className="mt-6 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-lg transition-all"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Filter top priorities according to filter bar
  const filteredPriorities = data.top_priorities.filter((p) => {
    if (selectedDomain !== 'ALL' && p.domain.toUpperCase() !== selectedDomain.toUpperCase()) return false;
    if (selectedSeverity !== 'ALL' && p.severity.toUpperCase() !== selectedSeverity.toUpperCase()) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
              <LayoutDashboard className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-100 tracking-tight">Executive Cloud Operations Command Center</h1>
              <p className="text-xs text-slate-400">Unified C-Suite Operations Intelligence across Health, Reliability, Security, FinOps & Risk</p>
            </div>
          </div>
        </div>

        {/* Global Controls & Export */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            id="refresh-overview-btn"
            onClick={fetchOverview}
            className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold rounded-lg flex items-center gap-2 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
          <button
            id="export-csv-btn"
            onClick={handleExportCsv}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-2 transition-all"
          >
            <FileText className="w-3.5 h-3.5 text-emerald-400" /> Export CSV
          </button>
          <button
            id="export-pdf-btn"
            onClick={handleExportPdf}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
          >
            <Download className="w-3.5 h-3.5" /> Export Executive PDF
          </button>
        </div>
      </div>

      {/* Mode Indicator Banner */}
      <div className="px-4 py-2.5 bg-indigo-950/40 border border-indigo-500/30 rounded-lg flex items-center justify-between text-xs">
        <span className="font-mono text-indigo-300 flex items-center gap-2 font-semibold">
          <Cpu className="w-4 h-4 text-indigo-400" /> {data.mode_indicator}
        </span>
        <span className="text-[11px] text-slate-400 font-mono">Live Deterministic Aggregation</span>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-slate-900/60 border border-slate-800/60 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <Filter className="w-4 h-4 text-indigo-400" /> Dashboard Filters:
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Provider Filter */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Provider:</span>
            <select
              id="filter-provider"
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-xs font-semibold rounded-md px-2.5 py-1.5 focus:border-indigo-500 outline-none"
            >
              <option value="ALL">All Cloud Providers</option>
              <option value="AWS">AWS</option>
              <option value="AZURE">Azure</option>
              <option value="GCP">GCP</option>
              <option value="KUBERNETES">Kubernetes</option>
            </select>
          </div>

          {/* Domain Filter */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Domain:</span>
            <select
              id="filter-domain"
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-xs font-semibold rounded-md px-2.5 py-1.5 focus:border-indigo-500 outline-none"
            >
              <option value="ALL">All Domains</option>
              <option value="INCIDENT">Incident & SRE</option>
              <option value="SECURITY">Security</option>
              <option value="FINOPS">FinOps & Cost</option>
              <option value="CAPACITY">Capacity & Saturation</option>
              <option value="GOVERNANCE">FinOps Governance</option>
            </select>
          </div>

          {/* Severity Filter */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Severity:</span>
            <select
              id="filter-severity"
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-xs font-semibold rounded-md px-2.5 py-1.5 focus:border-indigo-500 outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical (P0)</option>
              <option value="HIGH">High (P1)</option>
              <option value="MEDIUM">Medium (P2)</option>
              <option value="LOW">Low (P3)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Row 1: Executive Health Gauge & Executive Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ExecutiveHealthGauge health={data.health_score} />
        <ExecutiveSummaryCard summary={data.summary} onRefresh={fetchOverview} />
      </div>

      {/* Row 2: Key Executive Metrics Grid */}
      <KeyMetricsGrid metrics={data.metrics} />

      {/* Row 3: Prioritized Action Queue & Provider Health Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TopPrioritiesQueue priorities={filteredPriorities} />
        </div>
        <div>
          <ProviderHealthGrid providers={data.provider_health} />
        </div>
      </div>

      {/* Row 4: Operational Trends & Service Health Map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <OperationalTrendsChart trends={data.operational_trends} />
        <ExecutiveServiceHealthMap services={services} />
      </div>

      {/* Row 5: Cloud Risk Matrix & What Changed Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CloudRiskMatrixTable matrix={data.risk_matrix} />
        <WhatChangedTable changes={data.what_changed} />
      </div>

      {/* Row 6: Executive Timeline Feed & Recommended Actions List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ExecutiveTimelineFeed events={timelineEvents} />
        <RecommendedActionsList recommendations={recommendations} />
      </div>
    </div>
  );
};
