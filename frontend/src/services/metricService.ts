/**
 * Frontend Service Client for Real-Time Observability
 */

import apiClient from "@/lib/api";
import type { MetricCurrentResponse, MetricHistoryResponse } from "@/types/metric";

export const metricService = {
  async getCurrent(): Promise<MetricCurrentResponse> {
    const response = await apiClient.get<MetricCurrentResponse>("/metrics/current");
    return response.data;
  },

  async getHistory(limit: number = 300): Promise<MetricHistoryResponse> {
    const response = await apiClient.get<MetricHistoryResponse>("/metrics/history", {
      params: { limit },
    });
    return response.data;
  },
};
