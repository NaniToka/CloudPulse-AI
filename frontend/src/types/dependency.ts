/**
 * TypeScript Interfaces for AI Service Dependency & Root-Cause Intelligence Engine.
 */

export interface ServiceNode {
  id: string;
  organization_id?: string | null;
  name: string;
  type: string; // "service", "database", "queue", "api", "cache", "gateway"
  environment: string;
  region: string;
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL' | 'UNKNOWN';
  health_score: number; // 0 - 100
  error_rate: number; // %
  latency_p99_ms: number;
  request_rate: number;
  active_incidents_count: number;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ServiceDependency {
  id: string;
  organization_id?: string | null;
  source_service_id?: string | null;
  target_service_id?: string | null;
  source_service: string;
  target_service: string;
  dependency_type: string; // "http", "grpc", "database", "queue", "internal"
  protocol: string;
  discovered_from: string; // "traces", "logs", "metrics", "kubernetes", "cloud_resources", "service_catalog"
  confidence: number; // 0.0 - 1.0
  latency_ms: number;
  error_rate: number;
  request_rate: number;
  call_count: number;
  error_count: number;
  evidence_count: number;
  evidence_metadata?: Record<string, any>;
  last_seen_at: string;
}

export interface DependencyGraph {
  nodes: ServiceNode[];
  edges: ServiceDependency[];
  total_nodes: number;
  total_edges: number;
  critical_path: string[];
  unhealthy_services_count: number;
  generated_at: string;
}

export interface ServiceNodeDetail extends ServiceNode {
  upstream_dependencies: ServiceDependency[];
  downstream_dependents: ServiceDependency[];
  recent_incidents: Array<{
    id: string;
    title: string;
    severity: string;
    status: string;
    started_at?: string;
  }>;
  recent_alerts: Array<Record<string, any>>;
}

export interface ServiceHealth {
  service_id?: string | null;
  service_name: string;
  health_score: number;
  status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL' | 'UNKNOWN';
  error_rate: number;
  latency_p99_ms: number;
  active_incidents_count: number;
  dependency_health_penalty: number;
  factors: string[];
  evaluated_at: string;
}

export interface FailurePropagationHop {
  source: string;
  target: string;
  latency_increase_percent: number;
  error_rate: number;
  propagation_risk: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface BlastRadiusResult {
  root_component: string;
  directly_affected_resources: string[];
  indirectly_affected_resources: string[];
  affected_services: string[];
  dependency_depth: number;
  propagation_paths: string[][];
  propagation_hops: FailurePropagationHop[];
  estimated_user_impact: string;
  financial_risk_estimate: string;
  affected_endpoints: string[];
  affected_regions: string[];
  topology_graph: {
    nodes: Array<{
      id: string;
      label: string;
      type: string;
      status: string;
      health_score: number;
      is_root_cause: boolean;
      environment: string;
    }>;
    edges: Array<{
      source: string;
      target: string;
      protocol: string;
      type: string;
      confidence: number;
      latency_ms: number;
    }>;
  };
}

export interface RootCauseCandidate {
  service_name: string;
  score: number; // 0.0 - 1.0
  rank: number;
  temporal_score: number;
  dependency_score: number;
  anomaly_score: number;
  propagation_score: number;
  evidence: Array<{
    type: string;
    source: string;
    target: string;
    observation: string;
    timestamp: string;
    strength: number;
  }>;
  recommended_actions: Array<Record<string, any>>;
}

export interface RootCauseRankingResult {
  primary_root_cause: string;
  primary_score: number;
  confidence: number;
  candidates: RootCauseCandidate[];
  reasoning_summary: string;
  evidence_graph: Array<Record<string, any>>;
  blast_radius?: BlastRadiusResult | null;
  analysis_engine: 'gemini' | 'local';
  recommended_actions: Array<Record<string, any>>;
}

export interface DependencyDiscoveryResult {
  discovered_nodes_count: number;
  discovered_edges_count: number;
  updated_edges_count: number;
  sources_processed: string[];
  discovered_at: string;
}
