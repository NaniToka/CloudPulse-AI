export interface SloOverview {
  platform_reliability_score: number;
  slo_compliance_pct: number;
  total_services: number;
  healthy_services: number;
  at_risk_services: number;
  breached_services: number;
  active_violations: number;
  average_error_budget_remaining_pct: number;
  mode_indicator: string;
}

export interface ServiceReliability {
  service: string;
  scenario: string;
  indicator_type: string;
  target_slo: number;
  availability_pct: number;
  error_rate_pct: number;
  latency_p95_ms: number;
  throughput_rps: number;
  reliability_score: number;
  status: 'HEALTHY' | 'AT_RISK' | 'BREACHED';
  contributing_factors: string[];
}

export interface SliMetrics {
  service: string;
  indicator_type: string;
  total_events: number;
  good_events: number;
  bad_events: number;
  availability_pct: number;
  error_rate_pct: number;
  latency_p50_ms: number;
  latency_p90_ms: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
  throughput_rps: number;
  window: string;
  status: string;
}

export interface SloObjective {
  id: string;
  service: string;
  name: string;
  description?: string;
  indicator_type: string;
  target: number;
  target_threshold_ms?: number;
  window: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface ErrorBudget {
  service: string;
  target_slo: number;
  window_days: number;
  total_budget_sec: number;
  consumed_budget_sec: number;
  remaining_budget_sec: number;
  consumed_budget_pct: number;
  remaining_budget_pct: number;
  burn_rate_multiplier: number;
  status: 'HEALTHY' | 'WARNING' | 'EXHAUSTED';
}

export interface BurnRate {
  service: string;
  burn_rate_x: number;
  severity: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'CRITICAL';
  window_hours: number;
  observed_failure_rate: number;
  allowed_failure_rate: number;
  explanation: string;
}

export interface SloViolation {
  id: string;
  service: string;
  violation_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  target_value: number;
  actual_value: number;
  difference: number;
  duration_seconds: number;
  explanation: string;
  status: string;
  incident_id?: string;
}

export interface CorrelatedIncident {
  incident_id: string;
  title: string;
  service: string;
  severity: string;
  status: string;
  slo_impact: string;
  estimated_downtime_sec: number;
  error_budget_consumed_pct: number;
  created_at: string;
}

export interface SloForecast {
  service: string;
  target_slo: number;
  current_availability_pct: number;
  projected_month_end_slo_pct: number;
  projected_budget_consumed_pct: number;
  projected_remaining_budget_pct: number;
  days_to_exhaustion: number;
  projected_exhaustion_date: string;
  is_compliant_projected: boolean;
  confidence_pct: number;
}

export interface SloRecommendation {
  id: string;
  service: string;
  problem: string;
  impact: string;
  recommendation: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  expected_improvement: string;
}

export interface SloAnalyzeResult {
  overview: SloOverview;
  services_analyzed: number;
  critical_breaches_count: number;
  recommendations: SloRecommendation[];
  analysis_summary: string;
}
