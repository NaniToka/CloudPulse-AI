export interface ExecutiveHealth {
  overall_health_score: number;
  status: 'HEALTHY' | 'DEGRADED' | 'AT_RISK' | 'CRITICAL';
  base_score: number;
  penalty: number;
  contributing_factors: string[];
  slo_compliance_pct: number;
  security_score: number;
  finops_score: number;
  capacity_health: number;
  active_breaches: number;
}

export interface OperationalRisk {
  operational_risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  active_risk_factors_count: number;
  affected_services_count: number;
  affected_services: string[];
}

export interface IntelligenceInsight {
  id: string;
  timestamp: string;
  category: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  summary: string;
  affected_service?: string;
  affected_provider?: string;
  affected_region?: string;
  business_impact: string;
  technical_impact: string;
  confidence: number;
  recommended_action: string;
  source_system: string;
}

export interface ExecutiveBrief {
  summary: string;
  top_concern: string;
  business_impact: string;
  recommended_action: string;
  is_ai_powered: boolean;
  badge: string;
}

export interface TopRiskItem {
  rank: number;
  title: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  affected_service: string;
  reason: string;
  impact: string;
  recommended_action: string;
}

export interface TopOpportunityItem {
  id: string;
  title: string;
  source: string;
  impact: string;
  potential_savings_monthly?: number | null;
  recommended_action: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface ExecutiveTrendItem {
  metric: string;
  current: number;
  previous_period: number;
  percentage_change: number;
  trend_direction: 'IMPROVING' | 'STABLE' | 'DEGRADING';
}

export interface TimelineItem {
  timestamp: string;
  event: string;
  service: string;
  severity: string;
  source: string;
  impact: string;
}

export interface CommandCenterOverview {
  health: ExecutiveHealth;
  risk: OperationalRisk;
  brief: ExecutiveBrief;
  insights: IntelligenceInsight[];
  top_risks: TopRiskItem[];
  opportunities: TopOpportunityItem[];
  timeline: TimelineItem[];
  trends: ExecutiveTrendItem[];
  active_incidents_count: number;
  monthly_spend: number;
  potential_savings: number;
}

export interface CommandCenterAnalyzeResult {
  overview: CommandCenterOverview;
  analysis_summary: string;
  correlated_insights_count: number;
}
