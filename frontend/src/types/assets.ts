export interface AssetResourceItem {
  id: string;
  name: string;
  resource_type: string;
  service: string;
  provider: string;
  region: string;
  availability_zone?: string | null;
  environment: string;
  status: 'healthy' | 'warning' | 'critical' | 'stopped' | 'degraded';
  cpu_percent?: number | null;
  memory_percent?: number | null;
  disk_percent?: number | null;
  network_in_mbps?: number | null;
  network_out_mbps?: number | null;
  monthly_cost: number;
  risk_score: number;
  owner: string;
  lifecycle_state: 'ACTIVE' | 'IDLE' | 'DEGRADED' | 'ORPHANED' | 'DECOMMISSIONED';
  is_orphaned: boolean;
  security_findings_count: number;
  governance_compliance_status: 'COMPLIANT' | 'NON_COMPLIANT' | 'WAIVED';
  tags: Record<string, any>;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AssetOverviewResponse {
  total_resources: number;
  aws_count: number;
  azure_count: number;
  gcp_count: number;
  kubernetes_count: number;
  healthy_count: number;
  warning_count: number;
  critical_count: number;
  orphaned_count: number;
  idle_count: number;
  total_monthly_cost: number;
  total_potential_savings: number;
  mode_indicator: string;
  updated_at: string;
}

export interface AssetProviderStat {
  provider: string;
  resource_count: number;
  monthly_cost: number;
  percentage: number;
  health_score: number;
}

export interface AssetProviderDistributionResponse {
  providers: AssetProviderStat[];
}

export interface AssetServiceStat {
  service: string;
  provider: string;
  resource_count: number;
  monthly_cost: number;
}

export interface AssetServiceDistributionResponse {
  services: AssetServiceStat[];
}

export interface AssetRegionStat {
  region: string;
  provider: string;
  resource_count: number;
  monthly_cost: number;
  status: string;
}

export interface AssetRegionDistributionResponse {
  regions: AssetRegionStat[];
}

export interface AssetTypeStat {
  resource_type: string;
  count: number;
  total_cost: number;
}

export interface AssetTypeDistributionResponse {
  types: AssetTypeStat[];
}

export interface AssetRelationshipItem {
  id: string;
  source_id: string;
  source_name: string;
  target_id: string;
  target_name: string;
  relationship_type: string;
  direction: string;
  confidence: number;
}

export interface AssetTopologyNode {
  id: string;
  name: string;
  type: string;
  provider: string;
  region: string;
  status: string;
  cost: number;
}

export interface AssetTopologyEdge {
  source: string;
  target: string;
  label: string;
}

export interface AssetTopologyResponse {
  nodes: AssetTopologyNode[];
  edges: AssetTopologyEdge[];
}

export interface OrphanedResourceItem {
  resource_id: string;
  resource_name: string;
  provider: string;
  service: string;
  region: string;
  reason: string;
  monthly_cost: number;
  potential_savings: number;
  recommended_action: string;
}

export interface OrphanedResourcesResponse {
  total_orphaned: number;
  total_potential_savings: number;
  orphaned_resources: OrphanedResourceItem[];
}

export interface AssetDetailResponse {
  resource: AssetResourceItem;
  relationships: AssetRelationshipItem[];
  security_findings: Record<string, any>[];
  governance_violations: Record<string, any>[];
  finops_optimization?: Record<string, any> | null;
  related_incidents: Record<string, any>[];
  telemetry_summary: Record<string, any>;
}
