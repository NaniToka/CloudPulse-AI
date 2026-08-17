import apiClient from "@/lib/api";
import type {
  CloudCostListResponse,
  CostAnomaliesResponse,
  CostAnalyzeResponse,
  CostBudgetItem,
  CostBudgetListResponse,
  CostBudgetPayload,
  CostDriversResponse,
  CostExplorerResponse,
  CostForecastResponse,
  CostHealthScoreResponse,
  CostOverviewResponse,
  CostSavingsResponse,
  CostTrendsResponse,
  ExecutiveCostSummaryResponse,
  FinOpsReportResponse,
  PeriodComparisonResponse,
  ProviderCostsResponse,
  RecommendationItem,
  RecommendationsResponse,
  SavingsCenterResponse,
  ServiceCostsResponse,
} from "@/types/cost";

export const costService = {
  async getOverview(params?: { provider?: string; date_range?: string }): Promise<CostOverviewResponse> {
    const response = await apiClient.get<CostOverviewResponse>("/cost/overview", { params });
    return response.data;
  },

  async getTrends(params?: { provider?: string; date_range?: string }): Promise<CostTrendsResponse> {
    const response = await apiClient.get<CostTrendsResponse>("/cost/trends", { params });
    return response.data;
  },

  async getProviders(params?: { provider?: string }): Promise<ProviderCostsResponse> {
    const response = await apiClient.get<ProviderCostsResponse>("/cost/providers", { params });
    return response.data;
  },

  async getServiceCosts(params?: { provider?: string }): Promise<ServiceCostsResponse> {
    const response = await apiClient.get<ServiceCostsResponse>("/cost/services", { params });
    return response.data;
  },

  async getAnomalies(params?: { provider?: string }): Promise<CostAnomaliesResponse> {
    const response = await apiClient.get<CostAnomaliesResponse>("/cost/anomalies", { params });
    return response.data;
  },

  async getForecast(params?: { provider?: string }): Promise<CostForecastResponse> {
    const response = await apiClient.get<CostForecastResponse>("/cost/forecast", { params });
    return response.data;
  },

  async getBudgets(): Promise<CostBudgetListResponse> {
    const response = await apiClient.get<CostBudgetListResponse>("/cost/budgets");
    return response.data;
  },

  async createBudget(payload: CostBudgetPayload): Promise<CostBudgetItem> {
    const response = await apiClient.post<CostBudgetItem>("/cost/budgets", payload);
    return response.data;
  },

  async updateBudget(id: string, payload: CostBudgetPayload): Promise<CostBudgetItem> {
    const response = await apiClient.put<CostBudgetItem>(`/cost/budgets/${id}`, payload);
    return response.data;
  },

  async getRecommendations(status = "active"): Promise<RecommendationsResponse> {
    const response = await apiClient.get<RecommendationsResponse>("/cost/recommendations", {
      params: { status },
    });
    return response.data;
  },

  async getSavings(): Promise<CostSavingsResponse> {
    const response = await apiClient.get<CostSavingsResponse>("/cost/savings");
    return response.data;
  },

  async triggerAnalysis(): Promise<CostAnalyzeResponse> {
    const response = await apiClient.post<CostAnalyzeResponse>("/cost/analyze");
    return response.data;
  },

  async getResources(params?: {
    skip?: number;
    limit?: number;
    service?: string;
    region?: string;
    search?: string;
  }): Promise<CloudCostListResponse> {
    const response = await apiClient.get<CloudCostListResponse>("/cost/resources", { params });
    return response.data;
  },

  async updateRecommendationStatus(
    id: string,
    status: "active" | "dismissed" | "applied"
  ): Promise<RecommendationItem> {
    const response = await apiClient.patch<RecommendationItem>(`/cost/recommendations/${id}/status`, null, {
      params: { status },
    });
    return response.data;
  },

  async getHealthScore(params?: { provider?: string }): Promise<CostHealthScoreResponse> {
    const response = await apiClient.get<CostHealthScoreResponse>("/cost/health-score", { params });
    return response.data;
  },

  async getExecutiveSummary(params?: { provider?: string }): Promise<ExecutiveCostSummaryResponse> {
    const response = await apiClient.get<ExecutiveCostSummaryResponse>("/cost/executive-summary", { params });
    return response.data;
  },

  async getDrivers(params?: { provider?: string }): Promise<CostDriversResponse> {
    const response = await apiClient.get<CostDriversResponse>("/cost/drivers", { params });
    return response.data;
  },

  async getPeriodComparison(params?: { provider?: string }): Promise<PeriodComparisonResponse> {
    const response = await apiClient.get<PeriodComparisonResponse>("/cost/period-comparison", { params });
    return response.data;
  },

  async getExplorer(params?: { provider?: string }): Promise<CostExplorerResponse> {
    const response = await apiClient.get<CostExplorerResponse>("/cost/explorer", { params });
    return response.data;
  },

  async getSavingsCenter(): Promise<SavingsCenterResponse> {
    const response = await apiClient.get<SavingsCenterResponse>("/cost/savings-center");
    return response.data;
  },

  async generateReport(payload: { date_range?: string; provider?: string }): Promise<FinOpsReportResponse> {
    const response = await apiClient.post<FinOpsReportResponse>("/cost/reports/generate", payload);
    return response.data;
  },

  getPdfReportDownloadUrl(dateRange = "30_days", provider?: string): string {
    const p = provider ? `&provider=${encodeURIComponent(provider)}` : "";
    return `/api/v1/cost/reports/pdf?date_range=${encodeURIComponent(dateRange)}${p}`;
  },

  getExportCsvUrl(provider?: string): string {
    const p = provider ? `?provider=${encodeURIComponent(provider)}` : "";
    return `/api/v1/cost/export${p}`;
  },
};

