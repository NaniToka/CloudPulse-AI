export interface DailyCostItem {
  date: string;
  cost: number;
}

export interface ServiceCostItem {
  service: string;
  cost: number;
  percentage: number;
  resource_count: number;
  fill?: string;
}

export interface RegionCostItem {
  region: string;
  cost: number;
  percentage: number;
  resource_count: number;
}

export interface ProviderCostItem {
  provider: string;
  cost: number;
  percentage: number;
  resource_count: number;
}

export interface ProviderCostsResponse {
  providers: ProviderCostItem[];
  total_cost: number;
}

export interface CloudCostItem {
  id: string;
  resource_name: string;
  service: string;
  provider: string;
  region: string;
  cost: number;
  daily_cost: number;
  usage_amount: number;
  usage_unit: string;
  environment: string;
  status: "active" | "idle" | "overprovisioned" | string;
  tags: Record<string, string>;
  timestamp: string;
}

export interface CloudCostListResponse {
  items: CloudCostItem[];
  total: number;
}

export interface RecommendationItem {
  id: string;
  resource_id?: string | null;
  resource_name: string;
  service: string;
  recommendation_type: "idle_resource" | "wasted_resource" | "rightsizing" | "reserved_instance" | "auto_scaling" | string;
  title: string;
  description: string;
  current_cost: number;
  estimated_savings: number;
  effort_level: "low" | "medium" | "high" | string;
  risk_level: "low" | "medium" | "high" | string;
  status: "active" | "dismissed" | "applied" | string;
  ai_summary?: string | null;
  created_at: string;
}

export interface RecommendationsResponse {
  items: RecommendationItem[];
  total: number;
  total_savings: number;
}

export interface CostOverviewResponse {
  monthly_cost: number;
  previous_month_cost: number;
  percentage_change: number;
  projected_cost: number;
  potential_savings: number;
  efficiency_score: number;
  active_resources_count: number;
  idle_resources_count: number;
  daily_trend: DailyCostItem[];
  service_breakdown: ServiceCostItem[];
  region_breakdown: RegionCostItem[];
  provider_breakdown?: ProviderCostItem[];
  data_source?: string;
  environment?: string;
}

export interface CostTrendsResponse {
  daily_trend: DailyCostItem[];
  monthly_trend?: DailyCostItem[];
  projected_cost: number;
  trend_direction: string;
}

export interface CostAnomalyItem {
  id: string;
  anomaly_score: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  detected_date: string;
  provider: string;
  service: string;
  resource: string;
  expected_cost: number;
  actual_cost: number;
  difference: number;
  explanation: string;
}

export interface CostAnomaliesResponse {
  anomalies: CostAnomalyItem[];
  total_anomalies: number;
  critical_anomalies: number;
}

export interface CostForecastResponse {
  forecast_7_day: number;
  forecast_30_day: number;
  projected_month_end: number;
  confidence: number;
  historical_basis: string;
  trend_direction: string;
}

export interface CostBudgetItem {
  id: string;
  name: string;
  provider: string;
  service: string;
  environment: string;
  amount: number;
  current_spend: number;
  utilization_pct: number;
  projected_spend: number;
  remaining: number;
  period: string;
  threshold_status: "NORMAL" | "WARNING_50" | "WARNING_75" | "CRITICAL_90" | "EXCEEDED_100" | string;
  threshold_percentages: number[];
  thresholds_reached: number[];
  created_at: string;
  updated_at: string;
}

export interface CostBudgetPayload {
  name: string;
  amount: number;
  provider?: string;
  service?: string;
  environment?: string;
  period?: string;
  threshold_percentages?: number[];
}

export interface CostBudgetListResponse {
  budgets: CostBudgetItem[];
  total: number;
}

export interface CostSavingsResponse {
  total_monthly_savings: number;
  total_annual_savings: number;
  opportunity_count: number;
}

export interface CostAnalyzeResponse {
  cost_summary: string;
  highest_cost_services: string[];
  idle_resources: string[];
  wasted_resources: string[];
  optimization_suggestions: string[];
  reserved_instance_recommendations: string[];
  auto_scaling_recommendations: string[];
  estimated_monthly_savings: number;
  recommendations: RecommendationItem[];
  efficiency_score: number;
  analyzed_at: string;
  analysis_engine?: string;
}

export interface ServiceCostsResponse {
  services: ServiceCostItem[];
  total_cost: number;
}

export interface CostHealthScoreResponse {
  score: number;
  status: "Healthy" | "Watch" | "At Risk" | "Critical" | string;
  factors: string[];
  explanation: string;
}

export interface ExecutiveCostSummaryResponse {
  monthly_cost: number;
  previous_month_cost: number;
  percentage_change: number;
  summary_statements: string[];
}

export interface CostDriverItem {
  name: string;
  cost: number;
  reason: string;
}

export interface CostDriversResponse {
  top_provider: CostDriverItem;
  top_service: CostDriverItem;
  top_region: CostDriverItem;
  top_resource: CostDriverItem;
  fastest_growing_service: CostDriverItem;
  largest_anomaly: Record<string, unknown>;
  largest_savings_opportunity: Record<string, unknown>;
}

export interface ProviderPeriodChange {
  provider: string;
  current_cost: number;
  previous_cost: number;
  difference: number;
}

export interface ServicePeriodChange {
  service: string;
  current_cost: number;
  previous_cost: number;
  difference: number;
}

export interface PeriodComparisonResponse {
  current_spend: number;
  previous_spend: number;
  total_spend_difference: number;
  percentage_difference: number;
  provider_changes: ProviderPeriodChange[];
  service_changes: ServicePeriodChange[];
}

export interface CostExplorerNode {
  id: string;
  name: string;
  level: "provider" | "service" | "region" | "resource" | string;
  cost: number;
  percentage_of_total: number;
  resource_count: number;
  children?: CostExplorerNode[];
}

export interface CostExplorerResponse {
  nodes: CostExplorerNode[];
  total_cost: number;
}

export interface SavingsCenterResponse {
  total_monthly_savings: number;
  total_annual_savings: number;
  opportunity_count: number;
  average_savings_per_opportunity: number;
  by_provider: Array<{ provider: string; savings: number }>;
  by_category: Array<{ category: string; savings: number }>;
  by_service: Array<{ service: string; savings: number }>;
}

export interface FinOpsReportResponse {
  generated_at: string;
  date_range: string;
  data_source: string;
  health_score: CostHealthScoreResponse;
  executive_summary: string;
  summary_statements: string[];
  total_monthly_cost: number;
  previous_month_cost: number;
  percentage_change: number;
  projected_cost: number;
  potential_monthly_savings: number;
  potential_annual_savings: number;
  cost_drivers: CostDriversResponse;
  period_comparison: PeriodComparisonResponse;
  provider_breakdown: ProviderCostItem[];
  service_breakdown: ServiceCostItem[];
  region_breakdown: RegionCostItem[];
  anomalies: CostAnomalyItem[];
  forecast: CostForecastResponse;
  budget_status: Record<string, unknown>;
  budget_crossing_projection: Record<string, unknown>;
  savings_center: SavingsCenterResponse;
  recommendations: RecommendationItem[];
}

