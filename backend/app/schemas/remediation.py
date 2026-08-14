"""
Pydantic Schemas for Enterprise AIOps Automated Remediation & Action Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ── Action Definition ─────────────────────────────────────────────────────────


class RemediationActionItem(BaseModel):
    action_type: str
    domain: str
    provider: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    required_permissions: list[str]
    supports_dry_run: bool = True
    supports_simulation: bool = True
    supports_rollback: bool = True
    requires_approval: bool = True


# ── Remediation Plan / Action Request ─────────────────────────────────────────


class RemediationActionCreate(BaseModel):
    trigger_source: str = "incident_intelligence"
    source_event_id: str | None = None
    root_cause: str
    affected_resource: str
    provider: str = "AWS"
    environment: str = "production"
    action_type: str
    risk_level: str = "MEDIUM"
    expected_impact: str
    estimated_downtime_sec: int = 0
    estimated_cost_impact: float = 0.0
    execution_mode: str = "SIMULATION"  # DRY_RUN, SIMULATION, MANUAL, APPROVED, AUTOMATED


class RemediationPlanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    trigger_source: str
    source_event_id: str | None = None
    root_cause: str
    affected_resource: str
    provider: str
    environment: str
    action_type: str
    risk_level: str
    expected_impact: str
    estimated_downtime_sec: int
    estimated_cost_impact: float
    requires_approval: bool
    rollback_supported: bool
    execution_mode: str
    confidence_score: float
    status: str
    plan_details: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Dry-Run & Approvals ───────────────────────────────────────────────────────


class RemediationDryRunRequest(BaseModel):
    target_resource: str | None = None
    execution_mode: str = "DRY_RUN"


class RemediationDryRunResponse(BaseModel):
    plan_id: uuid.UUID
    action_type: str
    affected_resource: str
    execution_mode: str = "DRY_RUN"
    risk_level: str
    preconditions_passed: bool
    reasons: list[str]
    proposed_state_diff: dict[str, Any]
    requires_approval: bool
    simulation_message: str


class RemediationApprovalRequest(BaseModel):
    comments: str | None = Field(default=None, description="Approval rationale or comment")


class RemediationRejectionRequest(BaseModel):
    rejection_reason: str = Field(..., description="Reason for rejecting remediation plan")


class RemediationApprovalResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    approver_id: uuid.UUID | None = None
    approver_role: str
    approval_status: str  # APPROVED, REJECTED
    comments: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Execution ─────────────────────────────────────────────────────────────────


class RemediationExecuteRequest(BaseModel):
    execution_mode: str | None = Field(
        default=None, description="Optional override mode: DRY_RUN, SIMULATION, LIVE"
    )
    idempotency_key: str | None = Field(
        default=None, description="Optional idempotency key to prevent double execution"
    )


class RemediationExecutionResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    user_id: uuid.UUID | None = None
    idempotency_key: str
    execution_mode: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    precondition_result: dict[str, Any]
    execution_result: dict[str, Any]
    verification_result: dict[str, Any]
    previous_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    error_message: str | None = None
    rollback_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Policy Management ─────────────────────────────────────────────────────────


class RemediationPolicyCreate(BaseModel):
    name: str
    trigger_signal: str  # INCIDENT, ANOMALY, CAPACITY, FINOPS, SLO
    condition_logic: dict[str, Any] = Field(default_factory=dict)
    action_type: str
    risk_level: str = "MEDIUM"
    execution_mode: str = "APPROVED"
    cooldown_minutes: int = 5
    is_enabled: bool = True


class RemediationPolicyUpdate(BaseModel):
    name: str | None = None
    trigger_signal: str | None = None
    condition_logic: dict[str, Any] | None = None
    action_type: str | None = None
    risk_level: str | None = None
    execution_mode: str | None = None
    cooldown_minutes: int | None = None
    is_enabled: bool | None = None


class RemediationPolicyResponse(BaseModel):
    id: uuid.UUID
    name: str
    trigger_signal: str
    condition_logic: dict[str, Any]
    action_type: str
    risk_level: str
    execution_mode: str
    cooldown_minutes: int
    is_enabled: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Audit Trail & Effectiveness ───────────────────────────────────────────────


class RemediationAuditResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID | None = None
    execution_id: uuid.UUID | None = None
    actor_id: uuid.UUID | None = None
    action_type: str
    event_type: str
    target_resource: str
    provider: str
    execution_mode: str
    details: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RemediationEffectivenessItem(BaseModel):
    plan_id: str
    service_name: str
    action_type: str
    pre_action_metric: float
    post_action_metric: float
    improvement_pct: float
    verification_status: str  # IMPROVED, UNCHANGED, DEGRADED, INSUFFICIENT_DATA
    verification_window_minutes: int = 15


# ── Overview & AI Analysis ────────────────────────────────────────────────────


class RemediationOverviewResponse(BaseModel):
    pending_approvals_count: int
    active_executions_count: int
    completed_remediations_count: int
    failed_remediations_count: int
    rollback_available_count: int
    success_rate_pct: float
    automation_policy_count: int
    cooldown_active_count: int
    mode_indicator: str


class RemediationAnalyzeResult(BaseModel):
    analysis_engine: str
    badge: str
    is_ai_powered: bool
    executive_summary: str
    recommended_actions: list[dict[str, Any]]
    risk_assessment: str
    rollback_strategy: str
    verification_plan: str
    analyzed_at: datetime
