"""
Pydantic Schemas for FinOps Governance & Cost Control Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

# ── Policy Schemas ────────────────────────────────────────────────────────────


class CostPolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(
        default="SPENDING",
        description="BUDGET, SPENDING, RESOURCE, SERVICE, PROVIDER, REGION, WASTE, ANOMALY, FORECAST, KUBERNETES",
    )
    provider: str = Field(default="all", description="aws, azure, gcp, kubernetes, all")
    scope: str = Field(default="all", description="production, staging, development, all")
    metric: str = Field(
        ...,
        description="monthly_spend, daily_spend, resource_cost, waste_cost, anomaly_score, budget_utilization",
    )
    operator: str = Field(default=">", description=">, >=, <, <=, ==, !=")
    threshold_value: float = Field(..., description="Numerical threshold limit")
    severity: str = Field(default="MEDIUM", description="INFO, LOW, MEDIUM, HIGH, CRITICAL")
    enabled: bool = Field(default=True)

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid_ops = (">", ">=", "<", "<=", "==", "!=")
        if v not in valid_ops:
            raise ValueError(f"Operator must be one of: {', '.join(valid_ops)}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        v_upper = v.upper()
        valid_sevs = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")
        if v_upper not in valid_sevs:
            raise ValueError(f"Severity must be one of: {', '.join(valid_sevs)}")
        return v_upper


class CostPolicyCreate(CostPolicyBase):
    pass


class CostPolicyUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category: str | None = None
    provider: str | None = None
    scope: str | None = None
    metric: str | None = None
    operator: str | None = None
    threshold_value: float | None = None
    severity: str | None = None
    enabled: bool | None = None


class CostPolicyResponse(CostPolicyBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CostPolicyListResponse(BaseModel):
    policies: list[CostPolicyResponse]
    total: int


# ── Violation Schemas ─────────────────────────────────────────────────────────


class CostViolationResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    policy_name: str
    category: str
    severity: str
    provider: str
    service: str
    resource_id: str | None = None
    resource_name: str
    actual_value: float
    threshold_value: float
    difference: float
    status: str  # OPEN, ACKNOWLEDGED, IN_REVIEW, RESOLVED, EXEMPTED
    explanation: str
    recommended_action: str
    detected_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CostViolationListResponse(BaseModel):
    violations: list[CostViolationResponse]
    total: int
    critical_count: int
    high_count: int


class ViolationStatusUpdate(BaseModel):
    status: str  # OPEN, ACKNOWLEDGED, IN_REVIEW, RESOLVED, EXEMPTED

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_upper = v.upper()
        valid = ("OPEN", "ACKNOWLEDGED", "IN_REVIEW", "RESOLVED", "EXEMPTED")
        if v_upper not in valid:
            raise ValueError(f"Status must be one of: {', '.join(valid)}")
        return v_upper


# ── Exception Schemas ─────────────────────────────────────────────────────────


class PolicyExceptionCreate(BaseModel):
    policy_id: uuid.UUID
    scope: str = Field(default="all")
    reason: str = Field(..., min_length=5)
    expiration_date: datetime


class PolicyExceptionResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    scope: str
    reason: str
    requested_by: str
    approved_by: str | None = None
    status: str  # PENDING, APPROVED, REJECTED, EXPIRED
    expiration_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyExceptionListResponse(BaseModel):
    exceptions: list[PolicyExceptionResponse]
    total: int


class PolicyExceptionStatusUpdate(BaseModel):
    status: str  # PENDING, APPROVED, REJECTED
    approved_by: str | None = None


# ── Remediation Schemas ───────────────────────────────────────────────────────


class RemediationActionResponse(BaseModel):
    id: uuid.UUID
    violation_id: uuid.UUID | None = None
    action_type: str
    resource_name: str
    provider: str
    estimated_savings: float
    risk_level: str  # low, medium, high
    rollback_supported: bool
    execution_mode: str  # DRY_RUN, SIMULATED, LIVE
    approval_status: str  # PENDING, APPROVED, REJECTED, EXECUTED, ROLLED_BACK
    requested_by: str
    approved_by: str | None = None
    executed_at: datetime | None = None
    original_config: dict
    recommended_config: dict
    rollback_config: dict
    execution_result: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RemediationActionListResponse(BaseModel):
    remediations: list[RemediationActionResponse]
    total: int
    pending_approvals: int
    potential_savings: float


class RemediationRequestPayload(BaseModel):
    violation_id: uuid.UUID | None = None
    action_type: str = Field(
        ...,
        description="stop_idle_compute, resize_resource, delete_unattached_storage, reduce_log_retention, scale_down_k8s, remove_unused_ip, archive_snapshot, change_tier",
    )
    resource_name: str
    provider: str
    estimated_savings: float = Field(..., ge=0.0)
    risk_level: str = Field(default="low")
    execution_mode: str = Field(default="DRY_RUN", description="DRY_RUN, SIMULATED, LIVE")


class RemediationApprovePayload(BaseModel):
    approved_by: str | None = None
    status: str = Field(default="APPROVED", description="APPROVED, REJECTED")


class RemediationExecutePayload(BaseModel):
    execution_mode: str = Field(default="SIMULATED", description="DRY_RUN, SIMULATED, LIVE")


# ── Governance Overview & Score Schemas ───────────────────────────────────────


class ScoreComponent(BaseModel):
    name: str
    score: int
    weight_pct: int
    status: str  # OPTIMAL, ACCEPTABLE, RISK
    details: str


class GovernanceScoreResponse(BaseModel):
    overall_score: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    budget_compliance: int
    policy_compliance: int
    waste_compliance: int
    forecast_compliance: int
    components: list[ScoreComponent]
    explanation: str


class GovernanceOverviewResponse(BaseModel):
    governance_score: GovernanceScoreResponse
    total_policies: int
    active_policies: int
    open_violations: int
    critical_violations: int
    active_exceptions: int
    pending_remediations: int
    total_potential_savings: float
    mode_indicator: str = Field(
        default="DEMO / LOCAL MODE — Controlled Remediations Simulated",
        description="Execution mode indicator",
    )


# ── Audit Log Schemas ─────────────────────────────────────────────────────────


class FinOpsAuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_email: str
    action: str
    entity_type: str
    entity_id: str
    result: str
    metadata_json: dict
    timestamp: datetime

    model_config = {"from_attributes": True}


class FinOpsAuditLogListResponse(BaseModel):
    audit_logs: list[FinOpsAuditLogResponse]
    total: int
