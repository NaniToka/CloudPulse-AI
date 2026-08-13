export interface SliMetricsItem {
  total_requests: number;
  failed_requests: number;
  availability: number;
  error_rate: number;
  latency_p50_ms: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
  throughput_rps: number;
}

export interface SloItem {
  id: string;
  service: string;
  name: string;
  description?: string | null;
  indicator_type: "availability" | "latency" | "error_rate" | "throughput" | string;
  target: number;
  target_threshold_ms?: number | null;
  window: string;
  enabled: bool;
  current_sli: number;
  compliance_percentage: number;
  status: "HEALTHY" | "AT_RISK" | "BREACHED" | string;
  created_at: string;
  updated_at: string;
}

export interface SloCreatePayload {
  service: string;
  name: string;
  description?: string;
  indicator_type?: string;
  target: number;
  target_threshold_ms?: number;
  window?: string;
  enabled?: boolean;
}

export interface SloListResponse {
  slos: SloItem[];
  total: number;
}

export interface ErrorBudgetItem {
  service: string;
  target_slo: number;
  total_budget_pct: number;
  consumed_pct: number;
  remaining_pct: number;
  remaining_budget_units: number;
  status: "HEALTHY" | "AT_RISK" | "EXHAUSTED" | string;
}

export interface BurnRateItem {
  service: string;
  burn_1h: number;
  burn_6h: number;
  burn_24h: number;
  burn_7d: number;
  status: "NORMAL" | "ELEVATED" | "CRITICAL" | string;
}

export interface ServiceReliabilityItem {
  service: string;
  reliability_score: number;
  rating: "EXCELLENT" | "GOOD" | "DEGRADED" | "CRITICAL" | string;
  availability: number;
  latency_p95_ms: number;
  error_rate: number;
  throughput_rps: number;
  slo_status: "HEALTHY" | "AT_RISK" | "BREACHED" | string;
  error_budget_remaining_pct: number;
  burn_rate_status: "NORMAL" | "ELEVATED" | "CRITICAL" | string;
  active_incidents_count: number;
  trend: "IMPROVING" | "STABLE" | "DEGRADED" | string;
}

export interface ServiceReliabilityListResponse {
  services: ServiceReliabilityItem[];
  total: number;
}

export interface ReliabilityRiskItem {
  id: string;
  risk: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  service: string;
  metric: string;
  current_value: string;
  threshold: string;
  detected_at: string;
  explanation: string;
  recommended_action: string;
}

export interface ReliabilityRiskListResponse {
  risks: ReliabilityRiskItem[];
  total_risks: number;
  critical_risks: number;
}

export interface IncidentImpactItem {
  id: string;
  title: string;
  service: string;
  severity: string;
  status: string;
  started_at?: string | null;
  duration_minutes: number;
  slo_impact: string;
  budget_impact_pct: number;
}

export interface IncidentImpactListResponse {
  incidents: IncidentImpactItem[];
  total: number;
}

export interface DependencyImpactItem {
  dependency: string;
  target_service: string;
  health: "HEALTHY" | "DEGRADED" | "CRITICAL" | string;
  latency_ms: number;
  error_rate: number;
  affected_services: string[];
  reliability_risk: string;
}

export interface DependencyImpactListResponse {
  dependencies: DependencyImpactItem[];
  total: number;
}

export interface ForecastPeriod {
  availability: number;
  error_rate: number;
  latency_ms: number;
  slo_status: string;
}

export interface ReliabilityForecastResponse {
  forecast_24h: ForecastPeriod;
  forecast_7d: ForecastPeriod;
  forecast_30d: ForecastPeriod;
  confidence: number;
  historical_basis: string;
  status: string;
}

export interface SreRecommendationItem {
  id: string;
  service: string;
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  reason: string;
  evidence: string;
  recommended_action: string;
  expected_impact: string;
  confidence: number;
}

export interface SreRecommendationListResponse {
  recommendations: SreRecommendationItem[];
  total: number;
}

export interface SreOverviewResponse {
  overall_score: number;
  overall_rating: string;
  services_healthy: number;
  services_at_risk: number;
  slo_breaches: number;
  error_budget_remaining_avg: number;
  active_incidents_count: number;
  data_source?: string;
  environment?: string;
}

export interface SreAnalyzeResponse {
  executive_summary: string;
  critical_services: string[];
  error_budget_warnings: string[];
  sre_recommendations: SreRecommendationItem[];
  analyzed_at: string;
  analysis_engine?: string;
}
