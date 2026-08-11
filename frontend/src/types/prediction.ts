/**
 * TypeScript Type Definitions for AI Predictive Incident Detection Engine
 */

export type RiskLevel = "Critical" | "High" | "Medium" | "Low";
export type PredictionStatus =
  | "Active"
  | "Monitoring"
  | "Resolved"
  | "Expired"
  | "False_Positive"
  | "Mitigated"
  | "Dismissed"
  | "Triggered";

export interface MetricConcern {
  name: string;
  current_value: string;
  threshold: string;
  anomaly_trend: string;
  risk_impact: string;
}

export interface MetricForecastPoint {
  horizon: string;
  timestamp: string;
  predicted_value: number;
  lower_bound: number;
  upper_bound: number;
  confidence: number;
}

export interface MetricForecastResponse {
  metric_name: string;
  service: string;
  current_value: number;
  forecast_points: MetricForecastPoint[];
  historical_points: Array<{ timestamp: string; value: number }>;
  model_used: string;
  data_sufficiency: {
    samples: number;
    minimum_required: number;
    sufficient: boolean;
    confidence_factor: number;
  };
  generated_at: string;
}

export interface AnomalyEvent {
  id: string;
  organization_id?: string;
  service: string;
  metric_name: string;
  resource_id?: string;
  value: number;
  baseline_value: number;
  anomaly_score: number;
  severity: "NORMAL" | "WARNING" | "CRITICAL";
  direction: "SPIKE_HIGH" | "DROP_LOW" | "DRIFT" | "NORMAL";
  method: string;
  detected_at: string;
  details?: Record<string, any>;
}

export interface AnomalyDetectionResponse {
  metric_name: string;
  value: number;
  baseline_value: number;
  anomaly_score: number;
  severity: string;
  is_anomaly: boolean;
  direction: string;
  method_used: string;
  z_score: number;
  deviation_percent: number;
  explanation: string;
}

export interface CapacityRiskResponse {
  resource_name: string;
  current_value: number;
  capacity_limit: number;
  exhaustion_threshold: number;
  risk_score: number;
  risk_level: string;
  is_exhaustion_imminent: boolean;
  estimated_time_to_threshold_minutes?: number;
  rate_of_growth_per_minute: number;
  data_status: string;
  summary: string;
  recommended_mitigation: string;
}

export interface Prediction {
  id: string;
  title: string;
  service: string;
  metric_name?: string;
  resource_id?: string;
  environment?: string;
  region: string;
  prediction_score: number;
  failure_probability: number;
  expected_failure_time?: string;
  estimated_time_to_threshold_minutes?: number;
  risk_level: RiskLevel;
  status: PredictionStatus;
  trend_direction?: string;
  trend_strength?: number;
  rate_of_change?: number;
  anomaly_score?: number;
  affected_services: string[];
  likely_root_cause?: string;
  confidence_score: number;
  recommended_preventive_actions: string[];
  triggering_metrics: Record<string, any>;
  data_sufficiency?: Record<string, any>;
  forecast_points?: Array<{
    horizon: string;
    timestamp: string;
    predicted_value: number;
    lower_bound: number;
    upper_bound: number;
    confidence: number;
  }>;
  correlated_signals?: Array<{
    metric: string;
    current_value: number;
    baseline: number;
    anomaly_score: number;
    severity: string;
    direction: string;
    trend: string;
    explanation: string;
  }>;
  analysis_engine?: "gemini" | "local";
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

export interface PredictionAnalytics {
  total_predictions: number;
  active_risks: number;
  critical_risks: number;
  anomaly_events_count: number;
  predicted_failures: number;
  average_confidence: number;
  predictions_by_service: Record<string, number>;
  predictions_by_metric: Record<string, number>;
  predictions_by_risk: Record<string, number>;
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
  telemetry_map?: Record<string, number[]>;
}
