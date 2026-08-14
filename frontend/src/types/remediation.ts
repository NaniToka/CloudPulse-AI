export interface RemediationOverview {
  pending_approvals_count: number;
  active_executions_count: number;
  completed_remediations_count: number;
  failed_remediations_count: number;
  rollback_available_count: number;
  success_rate_pct: number;
  automation_policy_count: number;
  cooldown_active_count: number;
  mode_indicator: string;
}

export interface RemediationActionItem {
  action_type: str;
  domain: str;
  provider: str;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: str;
  required_permissions: str[];
  supports_dry_run: boolean;
  supports_simulation: boolean;
  supports_rollback: boolean;
  requires_approval: boolean;
}

export interface RemediationPlan {
  id: string;
  user_id?: string | null;
  trigger_source: string;
  source_event_id?: string | null;
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
  execution_mode: 'DRY_RUN' | 'SIMULATION' | 'MANUAL' | 'APPROVED' | 'AUTOMATED';
  confidence_score: number;
  status: 'PLANNED' | 'RECOMMENDED' | 'AWAITING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTING' | 'VERIFYING' | 'SUCCEEDED' | 'COMPLETED' | 'FAILED' | 'ROLLBACK_AVAILABLE' | 'ROLLED_BACK' | 'BLOCKED' | 'CANCELLED';
  plan_details: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface RemediationDryRunResult {
  plan_id: string;
  action_type: string;
  affected_resource: string;
  execution_mode: string;
  risk_level: string;
  preconditions_passed: boolean;
  reasons: string[];
  proposed_state_diff: Record<string, any>;
  requires_approval: boolean;
  simulation_message: string;
}

export interface RemediationExecution {
  id: string;
  plan_id: string;
  user_id?: string | null;
  idempotency_key: string;
  execution_mode: string;
  status: string;
  started_at?: string | null;
  completed_at?: string | null;
  precondition_result: Record<string, any>;
  execution_result: Record<string, any>;
  verification_result: Record<string, any>;
  previous_state?: Record<string, any> | null;
  new_state?: Record<string, any> | null;
  error_message?: string | null;
  rollback_status: string;
  created_at: string;
}

export interface RemediationPolicy {
  id: string;
  name: string;
  trigger_signal: string;
  condition_logic: Record<string, any>;
  action_type: string;
  risk_level: string;
  execution_mode: string;
  cooldown_minutes: number;
  is_enabled: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface RemediationAuditItem {
  id: string;
  plan_id?: string | null;
  execution_id?: string | null;
  actor_id?: string | null;
  action_type: string;
  event_type: string;
  target_resource: string;
  provider: string;
  execution_mode: string;
  details: Record<string, any>;
  created_at: string;
}

export interface RemediationEffectivenessItem {
  plan_id: string;
  service_name: string;
  action_type: string;
  pre_action_metric: number;
  post_action_metric: number;
  improvement_pct: number;
  verification_status: 'IMPROVED' | 'UNCHANGED' | 'DEGRADED' | 'INSUFFICIENT_DATA';
  verification_window_minutes: number;
}

export interface RemediationAnalyzeResult {
  analysis_engine: string;
  badge: string;
  is_ai_powered: boolean;
  executive_summary: string;
  recommended_actions: any[];
  risk_assessment: string;
  rollback_strategy: string;
  verification_plan: string;
  analyzed_at: string;
}
