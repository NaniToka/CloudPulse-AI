/**
 * TypeScript Type Definitions for AI Predictive Incident Detection Engine
 */

export type RiskLevel = "Critical" | "High" | "Medium" | "Low";
export type PredictionStatus = "Active" | "Mitigated" | "Dismissed" | "Triggered";

export interface MetricConcern {
  name: str;
  current_value: string;
  threshold: string;
  anomaly_trend: string;
  risk_impact: string;
}

export interface Prediction {
  id: string;
  title: string;
  service: string;
  region: string;
  prediction_score: number;
  failure_probability: number;
  expected_failure_time?: string;
  risk_level: RiskLevel;
  status: PredictionStatus;
  affected_services: string[];
  likely_root_cause?: string;
  confidence_score: number;
  recommended_preventive_actions: string[];
  triggering_metrics: Record<string, any>;
  created_at: string;
  updated_at: string;

  // Gemini AI detailed explanations
  ai_explanation?: string;
  ai_metrics_of_concern?: MetricConcern[];
  ai_historical_pattern_comparison?: string;
  ai_possible_impact?: string;
  ai_immediate_preventive_actions?: string[];
  ai_long_term_recommendations?: string[];
}

export interface PredictionListResponse {
  items: Prediction[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PredictionStats {
  predicted_failures: number;
  high_risk_services: number;
  avg_confidence_percent: number;
  prevented_downtime_hours: number;
}

export interface ServiceRiskItem {
  service: string;
  region: string;
  risk_level: RiskLevel;
  failure_probability: number;
  active_predictions_count: number;
}

export interface InfrastructureRiskHeatmap {
  items: ServiceRiskItem[];
}

export interface PredictionAnalyzePayload {
  services?: string[];
  lookback_hours?: number;
}
