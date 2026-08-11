/**
 * Frontend Service Dependency & Root-Cause Intelligence Service.
 * REST client for Service Topology, Blast Radius, Health Scoring, and RCA.
 */

import apiClient from "@/lib/api";
import type {
  BlastRadiusResult,
  DependencyDiscoveryResult,
  DependencyGraph,
  RootCauseRankingResult,
  ServiceHealth,
  ServiceNode,
  ServiceNodeDetail,
} from "@/types/dependency";

export interface GetGraphParams {
  environment?: string;
  region?: string;
  service?: string;
  depth?: number;
}

export interface ListServicesParams {
  environment?: string;
  region?: string;
  status?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
  page?: number;
  size?: number;
}

export interface ServiceListResponse {
  items: ServiceNode[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface DiscoveryPayload {
  time_window_minutes?: number;
  include_traces?: boolean;
  include_logs?: boolean;
  include_k8s?: boolean;
  include_cloud?: boolean;
}

export interface BlastRadiusPayload {
  service_name: string;
  depth?: number;
}

export interface RootCausePayload {
  service_name?: string;
  incident_id?: string;
  signals?: Array<Record<string, any>>;
}

export const dependencyService = {
  /**
   * Retrieves the full or filtered dependency topology graph.
   */
  async getGraph(params?: GetGraphParams): Promise<DependencyGraph> {
    const response = await apiClient.get<DependencyGraph>("/dependencies/graph", { params });
    return response.data;
  },

  /**
   * Lists paginated service nodes.
   */
  async listServices(params?: ListServicesParams): Promise<ServiceListResponse> {
    const response = await apiClient.get<ServiceListResponse>("/dependencies/services", { params });
    return response.data;
  },

  /**
   * Retrieves detailed service node attributes with upstream callers and downstream dependencies.
   */
  async getServiceDetail(serviceId: string): Promise<ServiceNodeDetail> {
    const response = await apiClient.get<ServiceNodeDetail>(`/dependencies/services/${serviceId}`);
    return response.data;
  },

  /**
   * Evaluates live calculated health score and degradation factors for a service.
   */
  async getServiceHealth(serviceId: string): Promise<ServiceHealth> {
    const response = await apiClient.get<ServiceHealth>(`/dependencies/services/${serviceId}/health`);
    return response.data;
  },

  /**
   * Triggers automatic dependency discovery across multi-modal telemetry.
   */
  async discoverDependencies(payload?: DiscoveryPayload): Promise<DependencyDiscoveryResult> {
    const response = await apiClient.post<DependencyDiscoveryResult>("/dependencies/discover", payload || {});
    return response.data;
  },

  /**
   * Simulates failure propagation and calculates blast radius for a service.
   */
  async calculateBlastRadius(payload: BlastRadiusPayload): Promise<BlastRadiusResult> {
    const response = await apiClient.post<BlastRadiusResult>("/dependencies/blast-radius", payload);
    return response.data;
  },

  /**
   * Ranks root cause candidates using topology and telemetry evidence.
   */
  async rankRootCauses(payload: RootCausePayload): Promise<RootCauseRankingResult> {
    const response = await apiClient.post<RootCauseRankingResult>("/dependencies/root-cause", payload);
    return response.data;
  },

  /**
   * Retrieves comprehensive topological root cause analysis for an incident.
   */
  async getIncidentAnalysis(incidentId: string): Promise<RootCauseRankingResult> {
    const response = await apiClient.get<RootCauseRankingResult>(`/dependencies/incidents/${incidentId}/analysis`);
    return response.data;
  },
};
