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
}
