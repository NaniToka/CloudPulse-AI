import apiClient from "@/lib/api";

export interface TwinResourceItem {
  id: string;
  name: string;
  type: string;
  status: string;
  provider?: string;
  cpu_pct?: number;
  hit_ratio?: number;
  connections?: number;
  p99_latency_ms?: number;
  traffic_rps?: number;
}

export interface InfrastructureTwinItem {
  id: string;
  user_id: string;
  name: string;
  status: "synchronized" | "simulating" | "degraded" | string;
  health_score: number;
  virtual_resources: TwinResourceItem[];
  topology_graph: {
    nodes: TwinResourceItem[];
    edges: Array<{ source: string; target: string }>;
  };
  total_services_count: number;
  active_simulations_count: number;
  created_at: string;
  updated_at: string;
}

export interface SimulationScenarioItem {
  id: string;
  twin_id: string;
  name: string;
  category: string;
  failure_type: string;
  target_resource: string;
  description: string;
  parameters: Record<string, any>;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  created_at: string;
}

export interface SimulationExecutionItem {
  id: string;
  twin_id: string;
  scenario_id: string;
  status: string;
  duration_seconds: number;
  risk_score: number;
  confidence_score: number;
  financial_impact_usd: number;
  estimated_recovery_minutes: number;
  affected_services: string[];
  blast_radius: {
    direct_impact?: string[];
    cascade_impact?: string[];
    latency_degradation_multiplier?: number;
    error_rate_spike_pct?: number;
  };
  predicted_timeline: Array<{ minute: string; event: string }>;
  recovery_steps: string[];
  started_at: string;
  completed_at?: string;
}

export interface BlastRadiusDetailItem {
  scenario_id: string;
  scenario_name: string;
  risk_score: number;
  affected_services: string[];
  financial_impact_usd: number;
  estimated_recovery_minutes: number;
  blast_radius: Record<string, any>;
  timeline: Array<{ minute: string; event: string }>;
  recovery_steps: string[];
}

export interface WhatIfResponseItem {
  id: string;
  query_text: string;
  impact_summary: string;
  predicted_risk_level: string;
  financial_risk_estimate: string;
  affected_components: string[];
  mitigations: string[];
  created_at: string;
}

export const twinService = {
  getTwin: async (): Promise<InfrastructureTwinItem> => {
    const response = await apiClient.get<InfrastructureTwinItem>("/twin");
    return response.data;
  },

  getTwinResources: async (): Promise<TwinResourceItem[]> => {
    const response = await apiClient.get<TwinResourceItem[]>("/twin/resources");
    return response.data;
  },

  getScenarios: async (params?: { category?: string }): Promise<SimulationScenarioItem[]> => {
    const response = await apiClient.get<SimulationScenarioItem[]>("/twin/simulations", { params });
    return response.data;
  },

  createScenario: async (payload: Partial<SimulationScenarioItem>): Promise<SimulationScenarioItem> => {
    const response = await apiClient.post<SimulationScenarioItem>("/twin/simulations", payload);
    return response.data;
  },

  runSimulation: async (scenarioId: string): Promise<SimulationExecutionItem> => {
    const response = await apiClient.post<SimulationExecutionItem>(`/twin/simulations/${scenarioId}/run`);
    return response.data;
  },

  getHistory: async (): Promise<SimulationExecutionItem[]> => {
    const response = await apiClient.get<SimulationExecutionItem[]>("/twin/simulations/history");
    return response.data;
  },

  getBlastRadius: async (scenarioId: string): Promise<BlastRadiusDetailItem> => {
    const response = await apiClient.get<BlastRadiusDetailItem>(`/twin/blast-radius/${scenarioId}`);
    return response.data;
  },

  askWhatIf: async (query: string): Promise<WhatIfResponseItem> => {
    const response = await apiClient.post<WhatIfResponseItem>("/twin/what-if", { query });
    return response.data;
  },
};
