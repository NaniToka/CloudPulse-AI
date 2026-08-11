/**
 * Frontend Incident Service — REST client calls for Enterprise Incident Command Center & RCA Platform
 */

import apiClient from "@/lib/api";
import type {
  BlastRadius,
  Incident,
  IncidentAcknowledgePayload,
  IncidentAIAnalysis,
  IncidentAnalytics,
  IncidentCorrelationPayload,
  IncidentCorrelationResponse,
  IncidentCreatePayload,
  IncidentListResponse,
  IncidentRemediatePayload,
  IncidentRemediateResponse,
  IncidentResolvePayload,
  IncidentStats,
  IncidentTimelineEventPayload,
  IncidentUpdatePayload,
  RCAData,
  TimelineEvent,
} from "@/types/incident";

export interface GetIncidentsParams {
  status?: string;
  severity?: string;
  priority?: string;
  service?: string;
  environment?: string;
  region?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
  page?: number;
  size?: number;
  page_size?: number;
}

export const incidentService = {
  async getIncidents(params?: GetIncidentsParams): Promise<IncidentListResponse> {
    const response = await apiClient.get<IncidentListResponse>("/incidents", { params });
    return response.data;
  },

  async getActiveIncidents(): Promise<Incident[]> {
    const response = await apiClient.get<Incident[]>("/incidents/active");
    return response.data;
  },

  async getStats(): Promise<IncidentStats> {
    const response = await apiClient.get<IncidentStats>("/incidents/stats");
    return response.data;
  },

  async getIncidentById(id: string): Promise<Incident> {
    const response = await apiClient.get<Incident>(`/incidents/${id}`);
    return response.data;
  },

  async declareIncident(payload: Partial<IncidentCreatePayload>): Promise<Incident> {
    const response = await apiClient.post<Incident>("/incidents/declare", payload);
    return response.data;
  },

  async createIncident(payload: IncidentCreatePayload): Promise<Incident> {
    const response = await apiClient.post<Incident>("/incidents", payload);
    return response.data;
  },

  async updateIncident(id: string, payload: IncidentUpdatePayload): Promise<Incident> {
    const response = await apiClient.put<Incident>(`/incidents/${id}`, payload);
    return response.data;
  },

  async acknowledgeIncident(id: string, payload?: IncidentAcknowledgePayload): Promise<Incident> {
    const response = await apiClient.post<Incident>(`/incidents/${id}/acknowledge`, payload || {});
    return response.data;
  },

  async investigateIncident(id: string, payload?: Record<string, any>): Promise<Incident> {
    const response = await apiClient.post<Incident>(`/incidents/${id}/investigate`, payload || {});
    return response.data;
  },

  async mitigateIncident(id: string, payload?: Record<string, any>): Promise<Incident> {
    const response = await apiClient.post<Incident>(`/incidents/${id}/mitigate`, payload || {});
    return response.data;
  },

  async resolveIncident(id: string, payload: IncidentResolvePayload): Promise<Incident> {
    const response = await apiClient.post<Incident>(`/incidents/${id}/resolve`, payload);
    return response.data;
  },

  async reanalyzeIncident(id: string): Promise<IncidentAIAnalysis> {
    const response = await apiClient.post<IncidentAIAnalysis>(`/incidents/${id}/analyze`);
    return response.data;
  },

  async getTimeline(id: string): Promise<TimelineEvent[]> {
    const response = await apiClient.get<TimelineEvent[]>(`/incidents/${id}/timeline`);
    return response.data;
  },

  async addTimelineEvent(id: string, payload: IncidentTimelineEventPayload): Promise<TimelineEvent> {
    const response = await apiClient.post<TimelineEvent>(`/incidents/${id}/timeline`, payload);
    return response.data;
  },

  async getImpact(id: string): Promise<BlastRadius> {
    const response = await apiClient.get<BlastRadius>(`/incidents/${id}/impact`);
    return response.data;
  },

  async getRootCause(id: string): Promise<RCAData> {
    const response = await apiClient.get<RCAData>(`/incidents/${id}/root-cause`);
    return response.data;
  },

  async correlateAlerts(payload: IncidentCorrelationPayload): Promise<IncidentCorrelationResponse> {
    const response = await apiClient.post<IncidentCorrelationResponse>("/incidents/correlate", payload);
    return response.data;
  },

  async executeRemediation(id: string, payload: IncidentRemediatePayload): Promise<IncidentRemediateResponse> {
    const response = await apiClient.post<IncidentRemediateResponse>(`/incidents/${id}/remediate`, payload);
    return response.data;
  },

  async deleteIncident(id: string): Promise<void> {
    await apiClient.delete(`/incidents/${id}`);
  },

  async getAnalytics(): Promise<IncidentAnalytics> {
    const response = await apiClient.get<IncidentAnalytics>("/incidents/analytics");
    return response.data;
  },
};
