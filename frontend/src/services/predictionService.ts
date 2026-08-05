/**
 * Frontend Service Client for Predictive Analytics
 */

import apiClient from "@/lib/api";
import type {
  Prediction,
  PredictionListResponse,
  PredictionStats,
  InfrastructureRiskHeatmap,
  PredictionAnalyzePayload,
} from "@/types/prediction";

export interface GetPredictionsParams {
  service?: string;
  region?: string;
  risk?: string;
  status?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
  page?: number;
  size?: number;
}

export const predictionService = {
  async getPredictions(params?: GetPredictionsParams): Promise<PredictionListResponse> {
    const response = await apiClient.get<PredictionListResponse>("/predictions", { params });
    return response.data;
  },

  async getPredictionHistory(params?: GetPredictionsParams): Promise<PredictionListResponse> {
    const response = await apiClient.get<PredictionListResponse>("/predictions/history", { params });
    return response.data;
  },

  async getStats(): Promise<PredictionStats> {
    const response = await apiClient.get<PredictionStats>("/predictions/stats");
    return response.data;
  },

  async getRiskHeatmap(): Promise<InfrastructureRiskHeatmap> {
    const response = await apiClient.get<InfrastructureRiskHeatmap>("/predictions/heatmap");
    return response.data;
  },

  async getPredictionById(id: string): Promise<Prediction> {
    const response = await apiClient.get<Prediction>(`/predictions/${id}`);
    return response.data;
  },

  async triggerAnalysis(payload: PredictionAnalyzePayload): Promise<Prediction> {
    const response = await apiClient.post<Prediction>("/predictions/analyze", payload);
    return response.data;
  },

  async updateStatus(id: string, status: string): Promise<Prediction> {
    const response = await apiClient.patch<Prediction>(`/predictions/${id}/status`, { status });
    return response.data;
  },
};
