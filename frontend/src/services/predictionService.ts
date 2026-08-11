/**
 * Frontend Service Client for Predictive AIOps & Anomaly Intelligence
 */

import apiClient from "@/lib/api";
import type {
  AnomalyDetectionResponse,
  AnomalyEvent,
  CapacityRiskResponse,
  InfrastructureRiskHeatmap,
  MetricForecastResponse,
  Prediction,
  PredictionAnalytics,
  PredictionAnalyzePayload,
  PredictionListResponse,
  PredictionStats,
} from "@/types/prediction";

export interface GetPredictionsParams {
  service?: string;
  resource?: string;
  metric?: string;
  environment?: string;
  region?: string;
  risk?: string;
  status?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
  page?: number;
  size?: number;
}

export interface ForecastPayload {
  service: string;
  metric_name: string;
  historical_values?: number[];
  horizons?: string[];
  step_minutes?: number;
}

export interface AnomalyPayload {
  service: string;
  metric_name: string;
  current_value?: number;
  historical_values?: number[];
  custom_critical_threshold?: number;
}

export interface CapacityPayload {
  service: string;
  resource_name: string;
  historical_values?: number[];
  custom_threshold?: number;
}

export const predictionService = {
  async getPredictions(params?: GetPredictionsParams): Promise<PredictionListResponse> {
    const response = await apiClient.get<PredictionListResponse>("/predictions", { params });
    return response.data;
  },

  async getStats(): Promise<PredictionStats> {
    const response = await apiClient.get<PredictionStats>("/predictions/stats");
    return response.data;
  },

  async getAnalytics(): Promise<PredictionAnalytics> {
    const response = await apiClient.get<PredictionAnalytics>("/predictions/analytics");
    return response.data;
  },

  async getRiskHeatmap(): Promise<InfrastructureRiskHeatmap> {
    const response = await apiClient.get<InfrastructureRiskHeatmap>("/predictions/heatmap");
    return response.data;
  },

  async getAnomalies(params?: { service?: string; severity?: string; page?: number; size?: number }): Promise<AnomalyEvent[]> {
    const response = await apiClient.get<AnomalyEvent[]>("/predictions/anomalies", { params });
    return response.data;
  },

  async detectAnomalies(payload: AnomalyPayload): Promise<AnomalyDetectionResponse> {
    const response = await apiClient.post<AnomalyDetectionResponse>("/predictions/anomalies", payload);
    return response.data;
  },

  async getForecast(payload: ForecastPayload): Promise<MetricForecastResponse> {
    const response = await apiClient.post<MetricForecastResponse>("/predictions/forecast", payload);
    return response.data;
  },

  async evaluateCapacity(payload: CapacityPayload): Promise<CapacityRiskResponse> {
    const response = await apiClient.post<CapacityRiskResponse>("/predictions/capacity", payload);
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

  async createIncidentFromPrediction(id: string, payload?: { severity?: string; title?: string }): Promise<any> {
    const response = await apiClient.post(`/predictions/${id}/create-incident`, payload || {});
    return response.data;
  },
};
