/**
 * Frontend Incident Service — REST client calls for Incident Management Center
 */

import apiClient from "@/lib/api";
import type {
  Incident,
  IncidentCreatePayload,
  IncidentUpdatePayload,
  IncidentResolvePayload,
  IncidentListResponse,
  IncidentAnalytics,
  IncidentAIAnalysis,
} from "@/types/incident";

export interface GetIncidentsParams {
  status?: string;
  severity?: string;
  priority?: string;
  service?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
  page?: number;
  size?: number;
}

export const incidentService = {
  async getIncidents(params?: GetIncidentsParams): Promise<IncidentListResponse> {
    const response = await apiClient.get<IncidentListResponse>("/incidents", { params });
    return response.data;
  },

  async getIncidentById(id: string): Promise<Incident> {
    const response = await apiClient.get<Incident>(`/incidents/${id}`);
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

  async resolveIncident(id: string, payload: IncidentResolvePayload): Promise<Incident> {
    const response = await apiClient.post<Incident>(`/incidents/${id}/resolve`, payload);
    return response.data;
  },

  async reanalyzeIncident(id: string): Promise<IncidentAIAnalysis> {
    const response = await apiClient.post<IncidentAIAnalysis>(`/incidents/${id}/analyze`);
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
