/**
 * TypeScript Type Definitions for Real-Time Observability Platform
 */

export interface K8sPodStatus {
  name: string;
  namespace: string;
  node: string;
  service: string;
  status: "Running" | "Pending" | "Failed" | "Rebuilding";
  cpu_percent: number;
  memory_mb: number;
  restarts: number;
  uptime: string;
}

export interface MetricPoint {
  id: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_traffic_mbps: number;
  active_users: number;
  requests_per_second: number;
  error_rate: number;
  response_time_ms: number;
  db_connections_active: number;
  db_connections_max: number;
  k8s_pods: K8sPodStatus[];
  timestamp: string;
}

export interface MetricCurrentResponse {
  current: MetricPoint;
  is_live: boolean;
  update_interval_ms: number;
}

export interface MetricHistoryResponse {
  history: MetricPoint[];
  total_points: number;
  buffer_size: number;
}

export interface TelemetryWebSocketMessage {
  event: "telemetry_update";
  data: MetricPoint;
}
