import apiClient from "@/lib/api";

export interface TelemetryEventItem {
  id: string;
  organization_id?: string;
  source: string;
  event_type: string;
  severity: "CRITICAL" | "ERROR" | "WARN" | "INFO" | string;
  timestamp: string;
  metadata?: Record<string, any>;
  raw_payload?: Record<string, any>;
}

export interface MetricRecordItem {
  id: string;
  resource_id: string;
  metric_name: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface TraceRecordItem {
  id: string;
  service_name: string;
  operation: string;
  duration: number;
  status: string;
  timestamp: string;
}

export interface TelemetryHealthItem {
  status: string;
  pipelines: Record<string, string>;
  events_ingested_total: number;
  metrics_ingested_total: number;
  traces_ingested_total: number;
  active_anomalies_count: number;
  ai_status: string;
  timestamp: string;
}

export interface AIOperationalSummaryItem {
  summary: string;
  root_cause_analysis: string;
  impacted_services: string[];
  confidence_score: number;
  recommended_mitigations: string[];
}

export const telemetryService = {
  ingestLog: async (payload: { source: string; level: string; message: string; service_name?: string }): Promise<TelemetryEventItem> => {
    const res = await apiClient.post<TelemetryEventItem>("/telemetry/logs", payload);
    return res.data;
  },

  ingestMetric: async (payload: { resource_id: string; metric_name: string; value: number; unit?: string }): Promise<MetricRecordItem> => {
    const res = await apiClient.post<MetricRecordItem>("/telemetry/metrics", payload);
    return res.data;
  },

  ingestTraces: async (payload: { service_name: string; spans: Array<{ operation: string; duration_ms: number; status?: string }> }): Promise<TraceRecordItem[]> => {
    const res = await apiClient.post<TraceRecordItem[]>("/telemetry/traces", payload);
    return res.data;
  },

  getEvents: async (params?: { limit?: number; severity?: string }): Promise<TelemetryEventItem[]> => {
    const res = await apiClient.get<TelemetryEventItem[]>("/telemetry/events", { params });
    return res.data;
  },

  getHealth: async (): Promise<TelemetryHealthItem> => {
    const res = await apiClient.get<TelemetryHealthItem>("/telemetry/health");
    return res.data;
  },

  getAISummary: async (): Promise<AIOperationalSummaryItem> => {
    const res = await apiClient.get<AIOperationalSummaryItem>("/telemetry/ai-summary");
    return res.data;
  },
};
