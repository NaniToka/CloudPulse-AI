export interface TopologyNodeItem {
  id: string;
  name: string;
  type: string;
  provider: string;
  region: string;
  environment: string;
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL' | 'UNKNOWN';
  health_score: number;
  monthly_cost: number;
  risk_score: number;
  security_findings_count: number;
  governance_status: string;
  active_incidents_count: number;
  metadata: Record<string, any>;
}

export interface TopologyEdgeItem {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  protocol: string;
  confidence: number;
  latency_ms?: number | null;
  error_rate?: number | null;
}

export interface TopologyOverviewResponse {
  total_nodes: number;
  total_edges: number;
  total_providers: number;
  total_regions: number;
  unhealthy_nodes_count: number;
  spof_count: number;
  total_monthly_cost: number;
  updated_at: string;
}

export interface TopologyGraphResponse {
  nodes: TopologyNodeItem[];
  edges: TopologyEdgeItem[];
  total_nodes: number;
  total_edges: number;
  generated_at: string;
}

export interface BlastRadiusAnalysisResponse {
  target_node_id: string;
  target_node_name: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  affected_node_count: number;
  affected_service_count: number;
  affected_resource_count: number;
  affected_providers: string[];
  affected_regions: string[];
  directly_affected_nodes: string[];
  indirectly_affected_nodes: string[];
  propagation_paths: string[][];
  estimated_impact_level: string;
  recommended_mitigation: string;
  generated_at: string;
}

export interface FailureSimulationRequest {
  node_id: string;
  failure_type: string;
}

export interface FailureSimulationResponse {
  target_node_id: string;
  target_node_name: string;
  failure_type: string;
  is_simulation: boolean;
  blast_radius: BlastRadiusAnalysisResponse;
  critical_path: string[];
  spof_detected: boolean;
  mitigation_steps: string[];
  simulated_at: string;
}

export interface SpofItem {
  node_id: string;
  node_name: string;
  node_type: string;
  provider: string;
  region: string;
  dependent_count: number;
  affected_services: string[];
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  reason: string;
  recommendation: string;
}

export interface SpofListResponse {
  total_spofs: number;
  spofs: SpofItem[];
}
