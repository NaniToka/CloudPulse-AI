/**
 * Enterprise Incident Management Center TypeScript Types
 */

export type SeverityLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "P0" | "P1" | "P2" | "P3";
export type PriorityLevel = "Critical" | "High" | "Medium" | "Low";
export type IncidentStatus =
  | "DETECTED"
  | "INVESTIGATING"
  | "IDENTIFIED"
  | "MITIGATING"
  | "RESOLVED"
  | "CLOSED"
  | "Open"
  | "Monitoring";

export interface SimilarIncident {
  id: string;
  title: string;
  similarity?: string;
  resolution?: string;
}

export interface TimelineEvent {
  id: string;
  incident_id: string;
  event_type:
    | "metric_anomaly"
    | "alert_triggered"
    | "trace_failure"
    | "log_error"
    | "incident_created"
    | "rca_identified"
    | "remediation_recommended"
    | "remediation_executed"
    | "status_changed"
    | "engineer_note";
  title: string;
  description?: string;
  source: string;
  metadata?: Record<string, any>;
  timestamp: string;
  created_by?: string;
}

export interface EvidenceItem {
  type: "metric" | "log" | "trace" | "alert" | "topology" | "kubernetes" | "cloud" | string;
  source: string;
  message: string;
  severity?: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  timestamp?: string;
  metric_value?: number;
  threshold?: number;
  details?: Record<string, any>;
}

export interface RecommendedAction {
  id: string;
  title: string;
  description: string;
  action_type: "scale" | "restart" | "config" | "circuit_breaker" | "rollback" | "runbook" | string;
  workflow_id?: string;
  automated: boolean;
  risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  parameters?: Record<string, any>;
}

export interface BlastRadius {
  incident_id?: string;
  root_component: string;
  directly_affected_resources?: string[];
  indirectly_affected_resources?: string[];
  affected_services: string[];
  dependency_depth: number;
  estimated_user_impact: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  financial_risk_estimate: string;
  topology_graph?: {
    nodes: Array<{ id: string; label: string; type: string; status: string }>;
    edges: Array<{ source: string; target: string; relationship?: string }>;
  };
}

export interface RCAData {
  incident_id: string;
  root_cause: string;
  confidence: number;
  evidence: EvidenceItem[];
  affected_components: string[];
  contributing_factors: string[];
  recommended_actions: RecommendedAction[];
  ai_summary?: string;
  ai_business_impact?: string;
}

export interface Incident {
  id: string;
  title: string;
  description?: string;
  severity: SeverityLevel;
  priority: PriorityLevel;
  status: IncidentStatus;
  source?: string;
  affected_service: string;
  affected_services: string[];
  affected_resources?: string[];
  affected_region?: string;
  assigned_engineer?: string;
  assigned_to?: string;
  created_by?: string;
  started_at?: string;
  detected_at?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  resolution_notes?: string;
  resolved_by?: string;

  // Analysis & Multi-modal fields
  confidence_score?: number;
  impact_score?: number;
  root_cause?: string;
  contributing_factors?: string[];
  evidence?: EvidenceItem[];
  correlation_metadata?: Record<string, any>;
  recommended_actions?: RecommendedAction[];
  blast_radius?: BlastRadius;
  timeline_events?: TimelineEvent[];

  // AI Diagnostic fields
  ai_summary?: string;
  ai_root_cause?: string;
  ai_business_impact?: string;
  ai_suggested_resolution?: string;
  ai_immediate_mitigation?: string;
  ai_long_term_prevention?: string[];
  ai_preventive_actions?: string[];
  ai_similar_incidents?: SimilarIncident[];
  // SLA, MTTR & Tracking
  resource_id?: string;
  environment?: string;
  correlation_score?: number;
  mttr_seconds?: number;
  sla_target_seconds?: number;
  sla_status?: "PENDING" | "AT_RISK" | "MET" | "BREACHED" | string;
  analysis_engine?: "gemini" | "local" | string;
}

export interface IncidentCreatePayload {
  title: string;
  description?: string;
  severity: SeverityLevel;
  priority: PriorityLevel;
  status: IncidentStatus;
  source?: string;
  affected_service: string;
  affected_services?: string[];
  affected_resources?: string[];
  affected_region?: string;
  assigned_engineer?: string;
  assigned_to?: string;
  created_by?: string;
  started_at?: string;
  detected_at?: string;
  auto_analyze?: boolean;
}

export interface IncidentUpdatePayload {
  title?: string;
  description?: string;
  severity?: SeverityLevel;
  priority?: PriorityLevel;
  status?: IncidentStatus;
  source?: string;
  affected_service?: string;
  affected_services?: string[];
  affected_resources?: string[];
  affected_region?: string;
  assigned_engineer?: string;
  assigned_to?: string;
  resolution_notes?: string;
}

export interface IncidentAcknowledgePayload {
  assigned_to?: string;
  notes?: string;
}

export interface IncidentResolvePayload {
  resolution_notes: string;
  resolved_by?: string;
}

export interface IncidentRemediatePayload {
  action_id: string;
  authorized_by?: string;
  override_parameters?: Record<string, any>;
}

export interface IncidentRemediateResponse {
  action_id: string;
  status: string;
  workflow_execution_id?: string;
  message: string;
  executed_at: string;
}

export interface IncidentCorrelationPayload {
  alerts: Array<Record<string, any>>;
  time_window_minutes?: number;
  organization_id?: string;
}

export interface IncidentCorrelationResponse {
  correlated_incidents_count: number;
  raw_alerts_processed: number;
  incidents: Incident[];
}

export interface IncidentTimelineEventPayload {
  event_type: string;
  title: string;
  description?: string;
  source?: string;
  metadata?: Record<string, any>;
}

export interface IncidentListResponse {
  items: Incident[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface IncidentStats {
  open_incidents: number;
  critical_incidents: number;
  avg_resolution_time_minutes: number;
  sla_compliance_percent: number;
}

export interface SeverityCount {
  severity: string;
  count: number;
}

export interface MonthlyTrendPoint {
  month: string;
  count: number;
  resolved_count: number;
}

export interface IncidentAnalytics {
  incidents_by_severity: SeverityCount[];
  mean_time_to_resolve_minutes: number;
  monthly_trend: MonthlyTrendPoint[];
  resolution_rate_percent: number;
  active_incidents: number;
  resolved_incidents: number;
  total_incidents: number;
  sla_compliance_percent: number;
}

export interface IncidentAIAnalysis {
  ai_summary: string;
  root_cause: string;
  ai_root_cause: string;
  ai_business_impact: string;
  ai_suggested_resolution: string;
  ai_immediate_mitigation: string;
  ai_long_term_prevention: string[];
  ai_preventive_actions: string[];
  ai_similar_incidents: SimilarIncident[];
  ai_estimated_resolution_time: string;
  ai_confidence_score: number;
}

export interface IncidentWebSocketEvent {
  event: string;
  incident_id?: string;
  data?: Incident | any;
  timestamp?: string;
}
