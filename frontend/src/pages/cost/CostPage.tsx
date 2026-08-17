import React, { useState, useEffect } from "react";
import { DollarSign, Download, RefreshCw, FileSpreadsheet, AlertCircle, Info, Filter, Calendar } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import MonthlyCostCard from "@/components/cost/MonthlyCostCard";
import CostTrendChart from "@/components/cost/CostTrendChart";
import CostByServiceChart from "@/components/cost/CostByServiceChart";
import CostByRegion from "@/components/cost/CostByRegion";
import AiRecommendationPanel from "@/components/cost/AiRecommendationPanel";
import EstimatedSavingsCard from "@/components/cost/EstimatedSavingsCard";
import OptimizationOpportunities from "@/components/cost/OptimizationOpportunities";
import ResourceTable from "@/components/cost/ResourceTable";
import CostLoadingSkeleton from "@/components/cost/CostLoadingSkeleton";
import FinOpsBudgetPanel from "@/components/cost/FinOpsBudgetPanel";
import CostAnomalyPanel from "@/components/cost/CostAnomalyPanel";
import CostForecastCard from "@/components/cost/CostForecastCard";
import ExecutiveHealthCard from "@/components/cost/ExecutiveHealthCard";
import CostDriversPanel from "@/components/cost/CostDriversPanel";
import InteractiveCostExplorer from "@/components/cost/InteractiveCostExplorer";
import SavingsCenterPanel from "@/components/cost/SavingsCenterPanel";

import { costService } from "@/services/costService";

import type {
  CostOverviewResponse,
  CostAnalyzeResponse,
  RecommendationItem,
  CloudCostItem,
  CostBudgetItem,
  CostAnomalyItem,
  CostForecastResponse,
  CostHealthScoreResponse,
  ExecutiveCostSummaryResponse,
  CostDriversResponse,
  PeriodComparisonResponse,
  CostExplorerResponse,
  SavingsCenterResponse,
} from "@/types/cost";

export default function CostPage() {
  const [selectedProvider, setSelectedProvider] = useState<string>("all");
  const [selectedDateRange, setSelectedDateRange] = useState<string>("30_days");

  const [overview, setOverview] = useState<CostOverviewResponse | null>(null);
  const [healthScore, setHealthScore] = useState<CostHealthScoreResponse | null>(null);
  const [executiveSummary, setExecutiveSummary] = useState<ExecutiveCostSummaryResponse | null>(null);
  const [drivers, setDrivers] = useState<CostDriversResponse | null>(null);
  const [comparison, setComparison] = useState<PeriodComparisonResponse | null>(null);
  const [explorer, setExplorer] = useState<CostExplorerResponse | null>(null);
  const [savingsCenter, setSavingsCenter] = useState<SavingsCenterResponse | null>(null);

  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [resources, setResources] = useState<CloudCostItem[]>([]);
  const [budgets, setBudgets] = useState<CostBudgetItem[]>([]);
  const [anomalies, setAnomalies] = useState<CostAnomalyItem[]>([]);
  const [forecast, setForecast] = useState<CostForecastResponse | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<CostAnalyzeResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = React.useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const filterParams = {
        provider: selectedProvider === "all" ? undefined : selectedProvider,
        date_range: selectedDateRange,
      };

      const [
        overviewData,
        healthData,
        summaryData,
        driversData,
        comparisonData,
        explorerData,
        savingsCenterData,
        recsData,
        resourcesData,
        budgetData,
        anomalyData,
        forecastData,
      ] = await Promise.all([
        costService.getOverview(filterParams),
        costService.getHealthScore(filterParams),
        costService.getExecutiveSummary(filterParams),
        costService.getDrivers(filterParams),
        costService.getPeriodComparison(filterParams),
        costService.getExplorer(filterParams),
        costService.getSavingsCenter(),
        costService.getRecommendations(),
        costService.getResources({ limit: 100, service: undefined }),
        costService.getBudgets(),
        costService.getAnomalies(filterParams),
        costService.getForecast(filterParams),
      ]);

      setOverview(overviewData);
      setHealthScore(healthData);
      setExecutiveSummary(summaryData);
      setDrivers(driversData);
      setComparison(comparisonData);
      setExplorer(explorerData);
      setSavingsCenter(savingsCenterData);
      setRecommendations(recsData.items);
      setResources(resourcesData.items);
      setBudgets(budgetData.budgets);
      setAnomalies(anomalyData.anomalies);
      setForecast(forecastData);
    } catch (err: any) {
      console.error("Failed to load cost data", err);
      setError(err?.response?.data?.detail || err?.response?.data?.error || "Failed to load cloud cost data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [selectedProvider, selectedDateRange]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRunAiAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      const res = await costService.triggerAnalysis();
      setAiAnalysis(res);
      if (res.recommendations && res.recommendations.length > 0) {
        setRecommendations(res.recommendations);
      } else {
        const updatedRecs = await costService.getRecommendations();
        setRecommendations(updatedRecs.items);
      }
    } catch (err: any) {
      console.error("Cost AI analysis failed", err);
      alert(err?.response?.data?.detail || err?.response?.data?.error || "AI Cost analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleStatusChange = async (id: string, status: "active" | "dismissed" | "applied") => {
    try {
      await costService.updateRecommendationStatus(id, status);
      setRecommendations((prev) => prev.filter((r) => r.id !== id));
      const updatedOverview = await costService.getOverview({ provider: selectedProvider === "all" ? undefined : selectedProvider });
      setOverview(updatedOverview);
    } catch (err) {
      console.error("Failed to update recommendation status", err);
    }
  };

  const handleExportPdf = () => {
    const url = costService.getPdfReportDownloadUrl(selectedDateRange, selectedProvider === "all" ? undefined : selectedProvider);
    window.open(url, "_blank");
  };

  const handleExportCsv = () => {
    const url = costService.getExportCsvUrl(selectedProvider === "all" ? undefined : selectedProvider);
    window.open(url, "_blank");
  };

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title="FinOps & Cost Intelligence"
          subtitle="Multi-Cloud spend analysis, cost anomaly detection & AI optimization"
        />
        <CostLoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title="FinOps & Cost Intelligence"
          subtitle="Multi-Cloud spend analysis, cost anomaly detection & AI optimization"
        />
        <div className="p-8 rounded-xl border border-rose-500/20 bg-rose-500/5 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
          <h3 className="text-base font-semibold text-rose-300">Unable to load cost optimizer</h3>
          <p className="text-xs text-rose-200/80 max-w-md mx-auto">{error}</p>
          <Button onClick={loadData} variant="outline" size="sm" className="mt-2 gap-2 border-rose-500/30 text-rose-300">
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <PageHeader
        title="FinOps & Cost Intelligence Center"
        subtitle="Executive multi-cloud spend optimization, health scoring, cost driver attribution & budget intelligence"
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {/* Provider Filter */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-bg-elevated border border-white/10 text-xs">
              <Filter className="w-3.5 h-3.5 text-muted-foreground" />
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="bg-transparent text-foreground font-medium focus:outline-none cursor-pointer"
              >
                <option value="all" className="bg-slate-900">All Providers</option>
                <option value="aws" className="bg-slate-900">AWS</option>
                <option value="azure" className="bg-slate-900">Azure</option>
                <option value="gcp" className="bg-slate-900">GCP</option>
                <option value="kubernetes" className="bg-slate-900">Kubernetes</option>
              </select>
            </div>

            {/* Date Range Filter */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-bg-elevated border border-white/10 text-xs">
              <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
              <select
                value={selectedDateRange}
                onChange={(e) => setSelectedDateRange(e.target.value)}
                className="bg-transparent text-foreground font-medium focus:outline-none cursor-pointer"
              >
                <option value="7_days" className="bg-slate-900">Last 7 Days</option>
                <option value="30_days" className="bg-slate-900">Last 30 Days</option>
                <option value="quarter" className="bg-slate-900">Current Quarter</option>
              </select>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleExportPdf}
              className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
            >
              <Download className="h-3.5 w-3.5 text-brand-blue" />
              Executive PDF Report
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCsv}
              className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
              Export CSV
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={loadData}
              className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Demo Data Notification Banner */}
      <div className="p-3 rounded-lg border border-amber-500/20 bg-amber-500/5 flex items-center justify-between text-xs font-mono text-amber-300">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-amber-400 shrink-0" />
          <span>Notice: Live Cloud Credentials Disconnected. Displaying deterministic local fixture dataset across AWS, Azure, GCP, and Kubernetes.</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-amber-500/20 text-[10px] font-bold">LOCAL FIXTURE DATA</span>
      </div>

      {/* 1. Executive Health Score Card & Intelligence Summary */}
      <ExecutiveHealthCard healthScore={healthScore} executiveSummary={executiveSummary} />

      {/* 2. Top Executive Key Metrics */}
      {overview && (
        <MonthlyCostCard
          monthlyCost={overview.monthly_cost}
          projectedCost={overview.projected_cost}
          potentialSavings={overview.potential_savings}
          efficiencyScore={overview.efficiency_score}
          percentageChange={overview.percentage_change}
        />
      )}

      {/* 3. Major Cost Drivers & Period Comparison */}
      <CostDriversPanel drivers={drivers} comparison={comparison} />

      {/* 4. Savings Center Panel */}
      <SavingsCenterPanel savingsCenter={savingsCenter} />

      {/* 5. Interactive Cost Explorer */}
      <InteractiveCostExplorer explorer={explorer} />

      {/* 6. Spend Forecast & Cost Anomalies */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-6">
          <CostForecastCard forecast={forecast} />
        </div>
        <div className="xl:col-span-6">
          <CostAnomalyPanel anomalies={anomalies} />
        </div>
      </div>

      {/* 7. Budget Intelligence Panel */}
      <FinOpsBudgetPanel budgets={budgets} />

      {/* 8. Charts Row (Cost Trend + Service Pie + Region Breakdown) */}
      {overview && (
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          <div className="xl:col-span-8 space-y-6">
            <CostTrendChart data={overview.daily_trend} />
            <CostByServiceChart services={overview.service_breakdown} />
          </div>

          <div className="xl:col-span-4 space-y-6">
            <CostByRegion regions={overview.region_breakdown} />
            <EstimatedSavingsCard
              potentialSavings={overview.potential_savings}
              onApplyAll={handleExportPdf}
            />
          </div>
        </div>
      )}

      {/* 9. AI Recommendation Panel */}
      <AiRecommendationPanel
        analysis={aiAnalysis}
        onAnalyze={handleRunAiAnalysis}
        isAnalyzing={isAnalyzing}
      />

      {/* 10. Optimization Opportunities (Cards) */}
      <OptimizationOpportunities
        recommendations={recommendations}
        onStatusChange={handleStatusChange}
      />

      {/* 11. Resource Cost Inventory Table */}
      <ResourceTable resources={resources} />
    </div>
  );
}

