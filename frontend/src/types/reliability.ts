export interface ReliabilityOverview {
  overall_reliability_score: number;
  services_healthy: number;
  services_at_risk: number;
  services_breached: number;
  slo_compliance_pct: number;
  critical_burn_rates_count: number;
  error_budget_remaining_pct: number;
  mode_indicator: string;
}

export interface MultiWindowBurnRateItem {
  window: string;
  burn_rate_x: number;
  severity: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'CRITICAL';
  explanation: string;
}

export interface ServiceReliabilityProfile {
  service_id: string;
  service_name: string;
  provider: string;
  region: string;
  availability_pct: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
  error_rate_pct: number;
  slo_target: number;
  current_slo: number;
  error_budget_total_sec: number;
  error_budget_remaining_sec: number;
  error_budget_consumed_pct: number;
  error_budget_remaining_pct: number;
  burn_rate: number;
  reliability_score: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'HEALTHY' | 'AT_RISK' | 'BREACHING' | 'BREACHED';
  top_recommendation: string;
}

export interface ErrorBudgetOverview {
  service_name: string;
  target_slo: number;
  total_budget_sec: number;
  consumed_budget_sec: number;
  remaining_budget_sec: number;
  consumed_budget_pct: number;
  remaining_budget_pct: number;
  burn_rate_multiplier: number;
  status: string;
}

export interface ReliabilityRiskItem {
  service_name: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  top_factors: string[];
}

export interface SloForecastItem {
  service?: string;
  forecast_status: 'VALID' | 'INSUFFICIENT_DATA';
  target_slo: number;
  current_availability_pct: number;
  projected_7_day_slo_pct?: number | null;
  projected_30_day_slo_pct?: number | null;
  projected_month_end_slo_pct?: number | null;
  projected_budget_consumed_pct: number;
  days_to_exhaustion: number;
  projected_exhaustion_date: string;
  is_compliant_projected: bool;
  confidence_pct: number;
  message?: string;
}

export interface DependencyImpactItem {
  service_name: string;
  upstream_dependencies: string[];
  downstream_dependencies: string[];
  dependency_health: string;
  dependency_correlation: string;
}

export interface ReliabilityIncidentItem {
  incident_id: string;
  title: string;
  service: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  slo_impact: string;
  error_budget_impact: string;
  duration_minutes: number;
  status: string;
}

export interface ReliabilityRecommendationItem {
  id: string;
  service: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  category: string;
  reason: string;
  evidence: string;
  recommended_action: string;
  expected_reliability_impact: string;
}

export interface ReliabilityAnalyzeResult {
  analysis_engine: string;
  badge: string;
  is_ai_powered: boolean;
  executive_summary: string;
  critical_services: string[];
  recommendations: ReliabilityRecommendationItem[];
  analyzed_at: string;
}

export interface ServiceDetailView {
  profile: ServiceReliabilityProfile;
  error_budget: ErrorBudgetOverview;
  multi_window_burn_rates: Record<string, MultiWindowBurnRateItem>;
  forecast: SloForecastItem;
  dependencies: DependencyImpactItem;
  incidents: ReliabilityIncidentItem[];
  anomalies_count: number;
  capacity_risk: string;
  security_risk_score: number;
  cost_impact_monthly: number;
  recommendations: ReliabilityRecommendationItem[];
}
