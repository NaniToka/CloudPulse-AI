export interface ScoreComponent {
  name: string;
  score: number;
  weight_pct: number;
  status: 'OPTIMAL' | 'ACCEPTABLE' | 'RISK';
  details: string;
}

export interface GovernanceScoreResponse {
  overall_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  budget_compliance: number;
  policy_compliance: number;
  waste_compliance: number;
  forecast_compliance: number;
  components: ScoreComponent[];
  explanation: string;
}

export interface GovernanceOverviewResponse {
  governance_score: GovernanceScoreResponse;
  total_policies: number;
  active_policies: number;
  open_violations: number;
  critical_violations: number;
  active_exceptions: number;
  pending_remediations: number;
  total_potential_savings: number;
  mode_indicator: string;
}

export interface CostPolicy {
  id: string;
  name: string;
  description?: string;
  category: string; // BUDGET, SPENDING, RESOURCE, SERVICE, PROVIDER, REGION, WASTE, ANOMALY, FORECAST, KUBERNETES
  provider: string;
  scope: string;
  metric: string;
  operator: string;
  threshold_value: number;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  enabled: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface CostPolicyCreatePayload {
  name: string;
  description?: string;
  category: string;
  provider: string;
  scope: string;
  metric: string;
  operator: string;
  threshold_value: number;
  severity: string;
  enabled?: boolean;
}

export interface CostViolation {
  id: string;
  policy_id: string;
  policy_name: string;
  category: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  provider: string;
  service: string;
  resource_id?: string;
  resource_name: string;
  actual_value: number;
  threshold_value: number;
  difference: number;
  status: 'OPEN' | 'ACKNOWLEDGED' | 'IN_REVIEW' | 'RESOLVED' | 'EXEMPTED';
  explanation: string;
  recommended_action: string;
  detected_at: string;
  updated_at: string;
}

export interface PolicyException {
  id: string;
  policy_id: string;
  scope: string;
  reason: string;
  requested_by: string;
  approved_by?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  expiration_date: string;
  created_at: string;
  updated_at: string;
}

export interface PolicyExceptionCreatePayload {
  policy_id: string;
  scope?: string;
  reason: string;
  expiration_date: string;
}

export interface RemediationAction {
  id: string;
  violation_id?: string;
  action_type: string;
  resource_name: string;
  provider: string;
  estimated_savings: number;
  risk_level: 'low' | 'medium' | 'high';
  rollback_supported: boolean;
  execution_mode: 'DRY_RUN' | 'SIMULATED' | 'LIVE';
  approval_status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXECUTED' | 'ROLLED_BACK';
  requested_by: string;
  approved_by?: string;
  executed_at?: string;
  original_config: Record<string, unknown>;
  recommended_config: Record<string, unknown>;
  rollback_config: Record<string, unknown>;
  execution_result?: string;
  created_at: string;
  updated_at: string;
}

export interface RemediationRequestPayload {
  violation_id?: string;
  action_type: string;
  resource_name: string;
  provider: string;
  estimated_savings: number;
  risk_level?: string;
  execution_mode?: string;
}

export interface FinOpsAuditLog {
  id: string;
  actor_email: string;
  action: string;
  entity_type: string;
  entity_id: string;
  result: string;
  metadata_json: Record<string, unknown>;
  timestamp: string;
}
