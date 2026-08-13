export interface HealthComponentItem {
  name: string;
  score: number;
  weight_pct: number;
  status: string;
  details: string;
}

export interface HealthScoreResponse {
  overall_score: number;
  reliability_score: number;
  security_score: number;
  cost_score: number;
  performance_score: number;
  capacity_score: number;
  governance_score: number;
  incident_health: number;
  risk_level: 'HEALTHY' | 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK' | 'CRITICAL';
  trend: 'IMPROVING' | 'STABLE' | 'WORSENING';
  components: HealthComponentItem[];
  explanation: string;
}

export interface ExecutiveSummaryResponse {
  summary_text: string;
  source: string;
  generated_at: string;
  key_highlights: string[];
}

export interface KeyExecutiveMetricsResponse {
  active_incidents: number;
  critical_incidents: number;
  unresolved_anomalies: number;
  security_findings: number;
  critical_security_findings: number;
  current_monthly_spend: number;
  projected_spend: number;
  potential_savings: number;
  budget_utilization_pct: number;
  capacity_risk_score: number;
  policy_violations: number;
  pending_remediations: number;
  unhealthy_services: number;
  kubernetes_risk_level: string;
}

export interface ExecutivePriorityItem {
  id: string;
  priority_score: number;
  priority_level: 'P0' | 'P1' | 'P2' | 'P3';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  domain: 'INCIDENT' | 'SECURITY' | 'FINOPS' | 'CAPACITY' | 'GOVERNANCE' | 'KUBERNETES' | 'PERFORMANCE';
  title: string;
  description: string;
  affected_resource: string;
  business_impact: string;
  financial_impact: string;
  recommended_action: string;
  status: string;
  created_at: string;
}

export interface ExecutivePriorityListResponse {
  priorities: ExecutivePriorityItem[];
  total: number;
  p0_count: number;
  p1_count: number;
}

export interface OperationalTrendItem {
  metric_name: string;
  domain: string;
  current_period: number;
  previous_period: number;
  percentage_change: number;
  direction: 'UP' | 'DOWN' | 'FLAT';
  trend_status: 'IMPROVING' | 'STABLE' | 'WORSENING' | 'INSUFFICIENT_DATA';
  unit: string;
}

export interface OperationalTrendsResponse {
  trends: OperationalTrendItem[];
}

export interface ProviderHealthItem {
  provider: 'AWS' | 'Azure' | 'GCP' | 'Kubernetes' | string;
  health_score: number;
  monthly_spend: number;
  active_incidents: number;
  security_risk_level: string;
  capacity_risk_score: number;
  policy_violations: number;
  service_count: number;
  trend: string;
}

export interface CloudProviderHealthResponse {
  providers: ProviderHealthItem[];
}

export interface ServiceHealthMapItem {
  id: string;
  name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL' | 'UNKNOWN';
  environment: string;
  provider: string;
  incident_count: number;
  anomaly_count: number;
  monthly_cost: number;
  security_findings_count: number;
  capacity_risk: string;
  dependencies_count: number;
  last_updated: string;
}

export interface ServiceHealthMapResponse {
  services: ServiceHealthMapItem[];
  healthy_count: number;
  degraded_count: number;
  critical_count: number;
}

export interface RiskMatrixItem {
  domain: string;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  severity: string;
  trend: string;
  impact_summary: string;
  recommended_action: string;
}

export interface CloudRiskMatrixResponse {
  matrix: RiskMatrixItem[];
}

export interface WhatChangedItem {
  category: string;
  metric: string;
  current_value: string;
  previous_value: string;
  change_type: 'INCREASE' | 'DECREASE' | 'NEW' | 'RESOLVED' | 'STABLE';
  significance: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface WhatChangedResponse {
  changes: WhatChangedItem[];
  period_days: number;
}

export interface ExecutiveTimelineEvent {
  id: string;
  timestamp: string;
  domain: string;
  severity: string;
  title: string;
  resource: string;
  status: string;
  details: string;
}

export interface ExecutiveAlertItem {
  id: string;
  severity: string;
  domain: string;
  title: string;
  message: string;
  timestamp: string;
}

export interface ExecutiveAlertsResponse {
  alerts: ExecutiveAlertItem[];
}

export interface ExecutiveRecommendationItem {
  id: string;
  domain: string;
  action: string;
  title: string;
  impact: string;
  risk_level: string;
  estimated_savings: number;
  suggested_owner: string;
  status: string;
}

export interface ExecutiveRecommendationsResponse {
  recommendations: ExecutiveRecommendationItem[];
}

export interface ExecutiveOverviewResponse {
  health_score: HealthScoreResponse;
  summary: ExecutiveSummaryResponse;
  metrics: KeyExecutiveMetricsResponse;
  top_priorities: ExecutivePriorityItem[];
  provider_health: ProviderHealthItem[];
  operational_trends: OperationalTrendItem[];
  risk_matrix: RiskMatrixItem[];
  what_changed: WhatChangedItem[];
  alerts: ExecutiveAlertItem[];
  mode_indicator: string;
}
