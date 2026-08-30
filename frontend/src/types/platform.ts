export interface DependencyHealthItem {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'not_configured' | 'configured' | 'demo_local_mode';
  latency_ms: number;
  last_checked: string;
  message: string;
  provider_mode?: string;
  cloud_credential_status?: string;
}

export interface SystemMetrics {
  cpu_usage_pct: number;
  process_memory_mb: number;
  system_memory_pct: number;
  process_uptime_seconds: number;
  total_requests: number;
  error_count: number;
  error_rate_pct: number;
  avg_latency_ms: number;
}

export interface SlowestEndpointItem {
  method: string;
  endpoint: string;
  avg_latency_ms: number;
  requests: number;
}

export interface ApiPerformanceSummary {
  requests_per_minute: number;
  avg_latency_ms: number;
  error_rate_pct: number;
  slowest_endpoints: SlowestEndpointItem[];
}

export interface SystemEventItem {
  timestamp: string;
  severity: 'INFO' | 'WARNING' | 'ERROR';
  component: string;
  message: string;
}

export interface EnvironmentInfo {
  environment: string;
  ai_mode: string;
  ai_mode_label: string;
  cloud_credential_status: string;
  demo_mode: boolean;
}

export interface PlatformHealthSummaryResponse {
  status: string;
  app: string;
  version: string;
  env: string;
  overall_health_score: number;
  overall_status: 'Healthy' | 'Degraded' | 'Critical';
  dependencies: Record<string, DependencyHealthItem>;
}

export interface PlatformHealthDetailedResponse {
  overall_health_score: number;
  overall_status: 'Healthy' | 'Degraded' | 'Critical';
  availability_pct: number;
  healthy_components_count: number;
  degraded_components_count: number;
  unhealthy_components_count: number;
  dependencies: Record<string, DependencyHealthItem>;
  system_metrics: SystemMetrics;
  api_performance: ApiPerformanceSummary;
  system_events: SystemEventItem[];
  environment_info: EnvironmentInfo;
}

