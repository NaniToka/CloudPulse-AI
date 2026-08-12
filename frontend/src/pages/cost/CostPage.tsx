import React, { useState, useEffect } from "react";
import { DollarSign, Download, RefreshCw, FileSpreadsheet, AlertCircle, Info } from "lucide-react";
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

import { costService } from "@/services/costService";
import { exportCostReportToPdf } from "@/lib/costPdfExport";
import { exportToCsv } from "@/lib/csvExport";

import type {
  CostOverviewResponse,
  CostAnalyzeResponse,
  RecommendationItem,
  CloudCostItem,
  CostBudgetItem,
  CostAnomalyItem,
  CostForecastResponse,
} from "@/types/cost";

export default function CostPage() {
  const [overview, setOverview] = useState<CostOverviewResponse | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [resources, setResources] = useState<CloudCostItem[]>([]);
  const [budgets, setBudgets] = useState<CostBudgetItem[]>([]);
  const [anomalies, setAnomalies] = useState<CostAnomalyItem[]>([]);
  const [forecast, setForecast] = useState<CostForecastResponse | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<CostAnalyzeResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [overviewData, recsData, resourcesData, budgetData, anomalyData, forecastData] = await Promise.all([
        costService.getOverview(),
        costService.getRecommendations(),
        costService.getResources({ limit: 100 }),
        costService.getBudgets(),
        costService.getAnomalies(),
        costService.getForecast(),
      ]);

      setOverview(overviewData);
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
  };

  useEffect(() => {
    loadData();
  }, []);

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
      const updatedOverview = await costService.getOverview();
      setOverview(updatedOverview);
    } catch (err) {
      console.error("Failed to update recommendation status", err);
    }
  };

  const handleExportPdf = () => {
    exportCostReportToPdf(overview, aiAnalysis, recommendations);
  };

  const handleExportCsv = () => {
    if (!resources || resources.length === 0) return;
    const csvRows = resources.map((r) => ({
      ResourceName: r.resource_name,
      Service: r.service,
      Provider: r.provider.toUpperCase(),
      Region: r.region,
      Environment: r.environment,
      MonthlyCost: r.cost,
      DailyCost: r.daily_cost,
      Status: r.status,
    }));
    exportToCsv("cloudpulse_cost_analysis.csv", csvRows);
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
        subtitle="Enterprise multi-cloud spend optimization, anomaly detection, forecasting & budget intelligence"
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              <span className="text-muted-foreground">Env:</span>
              <span className="text-foreground font-semibold">{overview?.environment || "Local Development"}</span>
              <span className="text-muted-foreground">•</span>
              <span className="text-muted-foreground">Provider:</span>
              <span className="text-brand-blue font-semibold">{overview?.data_source || "Demo Data — No Cloud Credentials Connected"}</span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleExportPdf}
              className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
            >
              <Download className="h-3.5 w-3.5" />
              Export PDF
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCsv}
              className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
            >
              <FileSpreadsheet className="h-3.5 w-3.5" />
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
          <span>Notice: Live Cloud Provider APIs disconnected. Displaying deterministic local fixture dataset across AWS, Azure, GCP, and Kubernetes.</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-amber-500/20 text-[10px] font-bold">LOCAL FIXTURE DATA</span>
      </div>

      {/* 1. Key Metrics & Monthly Cost Card */}
      {overview && (
        <MonthlyCostCard
          monthlyCost={overview.monthly_cost}
          projectedCost={overview.projected_cost}
          potentialSavings={overview.potential_savings}
          efficiencyScore={overview.efficiency_score}
          percentageChange={overview.percentage_change}
        />
      )}

      {/* 2. Spend Forecast & Cost Anomalies */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-6">
          <CostForecastCard forecast={forecast} />
        </div>
        <div className="xl:col-span-6">
          <CostAnomalyPanel anomalies={anomalies} />
        </div>
      </div>

      {/* 3. Budget Intelligence Panel */}
      <FinOpsBudgetPanel budgets={budgets} />

      {/* 4. Charts Row (Cost Trend + Service Pie + Region Breakdown) */}
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

      {/* 5. AI Recommendation Panel */}
      <AiRecommendationPanel
        analysis={aiAnalysis}
        onAnalyze={handleRunAiAnalysis}
        isAnalyzing={isAnalyzing}
      />

      {/* 6. Optimization Opportunities (Cards) */}
      <OptimizationOpportunities
        recommendations={recommendations}
        onStatusChange={handleStatusChange}
      />

      {/* 7. Resource Cost Inventory Table */}
      <ResourceTable resources={resources} />
    </div>
  );
}
