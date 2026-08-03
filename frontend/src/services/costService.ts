import apiClient from "@/lib/api";
import type {
  CostOverviewResponse,
  ServiceCostsResponse,
  RecommendationsResponse,
  CostAnalyzeResponse,
  CloudCostListResponse,
  RecommendationItem,
} from "@/types/cost";

export const costService = {
  async getOverview(): Promise<CostOverviewResponse> {
    const response = await apiClient.get<CostOverviewResponse>("/cost/overview");
    return response.data;
  },

  async getServiceCosts(): Promise<ServiceCostsResponse> {
    const response = await apiClient.get<ServiceCostsResponse>("/cost/services");
    return response.data;
  },

  async getRecommendations(status = "active"): Promise<RecommendationsResponse> {
    const response = await apiClient.get<RecommendationsResponse>("/cost/recommendations", {
      params: { status },
    });
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

  async updateRecommendationStatus(id: string, status: "active" | "dismissed" | "applied"): Promise<RecommendationItem> {
    const response = await apiClient.patch<RecommendationItem>(`/cost/recommendations/${id}/status`, null, {
      params: { status },
    });
    return response.data;
  },
};
