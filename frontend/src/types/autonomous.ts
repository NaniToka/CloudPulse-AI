export interface ActionDefinition {
  action_type: string;
  domain: string;
  provider: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  required_permissions: string[];
  supports_dry_run: boolean;
  supports_simulation: boolean;
  supports_rollback: boolean;
  requires_approval: boolean;
}

export interface RemediationPlan {
  id: string;
  trigger_source: string;
  source_event_id?: string;
  root_cause: string;
  affected_resource: string;
  provider: string;
  environment: string;
  action_type: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  expected_impact: string;
  estimated_downtime_sec: number;
  estimated_cost_impact: number;
  requires_approval: boolean;
  rollback_supported: boolean;
  execution_mode: 'DRY_RUN' | 'SIMULATED' | 'LIVE';
  confidence_score: number;
  status: 'PLANNED' | 'WAITING_APPROVAL' | 'APPROVED' | 'EXECUTING' | 'VERIFYING' | 'COMPLETED' | 'FAILED' | 'ROLLED_BACK' | 'BLOCKED';
  plan_details: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface RemediationExecution {
  id: string;
  plan_id: string;
  idempotency_key: string;
  execution_mode: 'DRY_RUN' | 'SIMULATED' | 'LIVE';
  status: 'QUEUED' | 'VALIDATING' | 'WAITING_APPROVAL' | 'EXECUTING' | 'VERIFYING' | 'COMPLETED' | 'FAILED' | 'ROLLED_BACK' | 'BLOCKED';
  started_at?: string;
  completed_at?: string;
  precondition_result: Record<string, any>;
  execution_result: Record<string, any>;
  verification_result: Record<string, any>;
  previous_state?: Record<string, any>;
  new_state?: Record<string, any>;
  error_message?: string;
  rollback_status: string;
  created_at: string;
}

export interface AutonomyPolicy {
  id: string;
  autonomy_level: number; // 0-4
  max_autonomous_risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  allowed_providers: string[];
  allowed_environments: string[];
  excluded_resources: string[];
  excluded_namespaces: string[];
  default_execution_mode: 'DRY_RUN' | 'SIMULATED' | 'LIVE';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RemediationAuditLog {
  id: string;
  plan_id?: string;
  execution_id?: string;
  actor_id?: string;
  action_type: string;
  event_type: string;
  target_resource: string;
  provider: string;
  execution_mode: string;
  details: Record<string, any>;
  created_at: string;
}

export interface AutonomousOverview {
  autonomy_level: number;
  execution_mode: string;
  active_remediations_count: number;
  total_plans_count: number;
  completed_remediations_count: number;
  success_rate_pct: number;
  verification_success_rate_pct: number;
  rollback_rate_pct: number;
  blocked_actions_count: number;
  incidents_prevented_est: number;
  mode_indicator: string;
}

export interface SimulationResult {
  action_type: string;
  affected_resource: string;
  provider: string;
  environment: string;
  execution_mode: string;
  preconditions: Record<string, any>;
  approval_requirement: Record<string, any>;
  simulated_verification: Record<string, any>;
  simulation_result: string;
  message: string;
}
