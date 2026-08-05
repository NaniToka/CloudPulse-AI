/**
 * TypeScript Type Definitions for Distributed Tracing Platform
 */

export interface Span {
  id: string;
  trace_id: string;
  span_id: string;
  parent_span_id?: string;
  service_name: string;
  operation_name: string;
  span_kind: "SERVER" | "CLIENT" | "INTERNAL" | "PRODUCER" | "CONSUMER";
  status_code: "OK" | "ERROR";
  duration_ms: number;
  start_time: string;
  end_time: string;
  attributes_json: Record<string, any>;
  events_json: any[];
}

export interface Trace {
  id: string;
  trace_id: string;
  name: string;
  root_service: string;
  http_method: string;
  http_status: number;
  duration_ms: number;
  status: "ok" | "error";
  span_count: number;
  created_at: string;
  spans: Span[];
  ai_analysis_json?: TraceAIAnalysis;
}

export interface TraceListResponse {
  items: Trace[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ServiceNode {
  id: string;
  label: string;
  type: "service" | "database" | "cache" | "gateway" | "external";
  status: "healthy" | "warning" | "critical";
  avg_latency_ms: number;
  rps: number;
  error_rate_percent: number;
}

export interface ServiceEdge {
  source: string;
  target: string;
  call_count: number;
  avg_duration_ms: number;
  error_rate_percent: number;
}

export interface ServiceMapResponse {
  nodes: ServiceNode[];
  edges: ServiceEdge[];
}

export interface ServiceMetrics {
  service_name: string;
  avg_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  requests_per_second: number;
  error_rate_percent: number;
  dependencies: string[];
  ai_summary: string;
}

export interface TraceAIAnalysis {
  trace_id: string;
  bottleneck_detected: boolean;
  slowest_service: string;
  root_cause: string;
  latency_breakdown: Record<string, number>;
  optimization_suggestions: string[];
  retry_recommendations: string[];
  scaling_suggestions: string[];
  performance_score: number;
  confidence_score: number;
}
