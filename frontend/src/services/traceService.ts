/**
 * Frontend Service Client for Distributed Tracing
 */

import apiClient from "@/lib/api";
import type {
  Trace,
  TraceListResponse,
  ServiceMapResponse,
  ServiceMetrics,
  TraceAIAnalysis,
} from "@/types/trace";

export interface GetTracesParams {
  service?: string;
  status?: string;
  min_duration_ms?: number;
  max_duration_ms?: number;
  search?: string;
  page?: number;
  size?: number;
}

export const traceService = {
  async getTraces(params?: GetTracesParams): Promise<TraceListResponse> {
    const response = await apiClient.get<TraceListResponse>("/traces", { params });
    return response.data;
  },

  async getTraceById(traceId: string): Promise<Trace> {
    const response = await apiClient.get<Trace>(`/traces/${traceId}`);
    return response.data;
  },

  async analyzeTrace(traceId: string): Promise<TraceAIAnalysis> {
    const response = await apiClient.post<TraceAIAnalysis>(`/traces/${traceId}/analyze`);
    return response.data;
  },

  async getServiceMap(): Promise<ServiceMapResponse> {
    const response = await apiClient.get<ServiceMapResponse>("/services/map");
    return response.data;
  },

  async getServiceMetrics(serviceName: string): Promise<ServiceMetrics> {
    const response = await apiClient.get<ServiceMetrics>(`/services/${encodeURIComponent(serviceName)}/metrics`);
    return response.data;
  },
};
