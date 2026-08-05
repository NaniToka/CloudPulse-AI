/**
 * Incident Management Center TypeScript Types
 */

export type SeverityLevel = "P0" | "P1" | "P2" | "P3";
export type PriorityLevel = "Critical" | "High" | "Medium" | "Low";
export type IncidentStatus = "Open" | "Investigating" | "Monitoring" | "Resolved" | "Closed";

export interface SimilarIncident {
  id: string;
  title: string;
  similarity?: string;
  resolution?: string;
}

export interface Incident {
  id: string;
  title: string;
  description?: string;
  severity: SeverityLevel;
  priority: PriorityLevel;
  status: IncidentStatus;
  affected_service: string;
  affected_services: string[];
  assigned_engineer?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  resolution_notes?: string;
  resolved_by?: string;

  // AI Diagnostic fields
  ai_summary?: string;
  ai_root_cause?: string;
  ai_business_impact?: string;
  ai_suggested_resolution?: string;
  ai_preventive_actions?: string[];
  ai_similar_incidents?: SimilarIncident[];
  ai_estimated_resolution_time?: string;
}

export interface IncidentCreatePayload {
  title: string;
  description?: string;
  severity: SeverityLevel;
  priority: PriorityLevel;
  status: IncidentStatus;
  affected_service: string;
  affected_services?: string[];
  assigned_engineer?: string;
  created_by?: string;
  auto_analyze?: boolean;
}

export interface IncidentUpdatePayload {
  title?: string;
  description?: string;
  severity?: SeverityLevel;
  priority?: PriorityLevel;
  status?: IncidentStatus;
  affected_service?: string;
  affected_services?: string[];
  assigned_engineer?: string;
  resolution_notes?: string;
}

export interface IncidentResolvePayload {
  resolution_notes: string;
  resolved_by?: string;
}

export interface IncidentListResponse {
  items: Incident[];
  total: number;
  page: number;
  size: number;
  pages: number;
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
}

export interface IncidentAIAnalysis {
  ai_summary: string;
  ai_root_cause: string;
  ai_business_impact: string;
  ai_suggested_resolution: string;
  ai_preventive_actions: string[];
  ai_similar_incidents: SimilarIncident[];
  ai_estimated_resolution_time: string;
}

export interface IncidentWebSocketEvent {
  event: "incident_created" | "severity_changed" | "incident_resolved" | "assignment_changed" | "status_changed";
  incident_id?: string;
  data?: Incident;
  timestamp?: string;
  old_severity?: string;
  new_severity?: string;
  old_engineer?: string;
  new_engineer?: string;
  old_status?: string;
  new_status?: string;
  resolution_notes?: string;
}
