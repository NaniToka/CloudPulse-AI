import apiClient from "@/lib/api";
import type {
  SreOverviewResponse,
  ServiceReliabilityListResponse,
  ServiceReliabilityItem,
  SliMetricsItem,
  SloListResponse,
  SloItem,
  SloCreatePayload,
  ErrorBudgetItem,
  BurnRateItem,
  ReliabilityRiskListResponse,
  IncidentImpactListResponse,
  DependencyImpactListResponse,
  ReliabilityForecastResponse,
  SreRecommendationListResponse,
  SreAnalyzeResponse,
} from "@/types/sre";

export const sreService = {
  async getOverview(): Promise<SreOverviewResponse> {
    const response = await apiClient.get<SreOverviewResponse>("/sre/overview");
    return response.data;
  },

  async getServices(sortBy = "worst_reliability"): Promise<ServiceReliabilityListResponse> {
    const response = await apiClient.get<ServiceReliabilityListResponse>("/sre/services", {
      params: { sort_by: sortBy },
    });
    return response.data;
  },

  async getServiceDetail(serviceName: string): Promise<ServiceReliabilityItem> {
    const response = await apiClient.get<ServiceReliabilityItem>(`/sre/services/${serviceName}`);
    return response.data;
  },

  async getSlis(service?: string): Promise<SliMetricsItem> {
    const response = await apiClient.get<SliMetricsItem>("/sre/slis", {
      params: { service },
    });
    return response.data;
  },

  async getSlos(params?: { service?: string; indicator_type?: string }): Promise<SloListResponse> {
    const response = await apiClient.get<SloListResponse>("/sre/slos", { params });
    return response.data;
  },

  async createSlo(payload: SloCreatePayload): Promise<SloItem> {
    const response = await apiClient.post<SloItem>("/sre/slos", payload);
    return response.data;
  },

  async updateSlo(id: string, payload: Partial<SloCreatePayload>): Promise<SloItem> {
    const response = await apiClient.put<SloItem>(`/sre/slos/${id}`, payload);
    return response.data;
  },

  async getErrorBudgets(): Promise<ErrorBudgetItem[]> {
    const response = await apiClient.get<ErrorBudgetItem[]>("/sre/error-budgets");
    return response.data;
  },

  async getBurnRates(): Promise<BurnRateItem[]> {
    const response = await apiClient.get<BurnRateItem[]>("/sre/burn-rates");
    return response.data;
  },

  async getRisks(severity?: string): Promise<ReliabilityRiskListResponse> {
    const response = await apiClient.get<ReliabilityRiskListResponse>("/sre/risks", {
      params: { severity },
    });
    return response.data;
  },

  async getIncidents(): Promise<IncidentImpactListResponse> {
    const response = await apiClient.get<IncidentImpactListResponse>("/sre/incidents");
    return response.data;
  },

  async getDependencies(): Promise<DependencyImpactListResponse> {
    const response = await apiClient.get<DependencyImpactListResponse>("/sre/dependencies");
    return response.data;
  },

  async getForecast(): Promise<ReliabilityForecastResponse> {
    const response = await apiClient.get<ReliabilityForecastResponse>("/sre/forecast");
    return response.data;
  },

  async getRecommendations(): Promise<SreRecommendationListResponse> {
    const response = await apiClient.get<SreRecommendationListResponse>("/sre/recommendations");
    return response.data;
  },

  async triggerAnalysis(): Promise<SreAnalyzeResponse> {
    const response = await apiClient.post<SreAnalyzeResponse>("/sre/analyze");
    return response.data;
  },
};
