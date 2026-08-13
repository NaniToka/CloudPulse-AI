"""
Pydantic Schemas for Autonomous Operations & Self-Healing Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ── Action Catalog Schemas ───────────────────────────────────────────────────


class ActionDefinitionResponse(BaseModel):
    action_type: str
    domain: str
    provider: str
    risk_level: str
    description: str
    required_permissions: list[str]
    supports_dry_run: bool
    supports_simulation: bool
    supports_rollback: bool
    requires_approval: bool


# ── Remediation Plan Schemas ─────────────────────────────────────────────────


class RemediationPlanCreate(BaseModel):
    trigger_source: str = Field(default="incident_intelligence")
    source_event_id: str | None = None
    root_cause: str
    affected_resource: str
    provider: str = Field(default="AWS")
    environment: str = Field(default="production")
    action_type: str
    risk_level: str = Field(default="MEDIUM")
    expected_impact: str
    estimated_downtime_sec: int = 0
    estimated_cost_impact: float = 0.0
    execution_mode: str = Field(default="SIMULATED")


class RemediationPlanResponse(BaseModel):
    id: uuid.UUID
    trigger_source: str
    source_event_id: str | None
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

    class Config:
        from_attributes = True


# ── Execution Schemas ─────────────────────────────────────────────────────────


class RemediationExecutionResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    idempotency_key: str
    execution_mode: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    precondition_result: dict[str, Any]
    execution_result: dict[str, Any]
    verification_result: dict[str, Any]
    previous_state: dict[str, Any] | None
    new_state: dict[str, Any] | None
    error_message: str | None
    rollback_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Policy & Maintenance Window Schemas ───────────────────────────────────────


class AutonomyPolicyUpdate(BaseModel):
    autonomy_level: int = Field(ge=0, le=4, default=1)
    max_autonomous_risk: str = Field(default="LOW")
    allowed_providers: list[str] = Field(default_factory=lambda: ["AWS", "Azure", "GCP", "Kubernetes"])
    allowed_environments: list[str] = Field(default_factory=lambda: ["development", "staging", "production"])
    excluded_resources: list[str] = Field(default_factory=list)
    excluded_namespaces: list[str] = Field(default_factory=list)
    default_execution_mode: str = Field(default="SIMULATED")
    is_active: bool = True


class AutonomyPolicyResponse(BaseModel):
    id: uuid.UUID
    autonomy_level: int
    max_autonomous_risk: str
    allowed_providers: list[str]
    allowed_environments: list[str]
    excluded_resources: list[str]
    excluded_namespaces: list[str]
    default_execution_mode: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaintenanceWindowCreate(BaseModel):
    title: str
    environment: str = Field(default="production")
    start_time: datetime
    end_time: datetime
    timezone: str = Field(default="UTC")
    block_all_actions: bool = True
    allowed_actions: list[str] = Field(default_factory=list)


class MaintenanceWindowResponse(BaseModel):
    id: uuid.UUID
    title: str
    environment: str
    start_time: datetime
    end_time: datetime
    timezone: str
    block_all_actions: bool
    allowed_actions: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Simulation & Audit Schemas ────────────────────────────────────────────────


class SimulationRequest(BaseModel):
    action_type: str
    affected_resource: str
    provider: str = Field(default="AWS")
    environment: str = Field(default="production")
    execution_mode: str = Field(default="SIMULATED")


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID | None
    execution_id: uuid.UUID | None
    actor_id: uuid.UUID | None
    action_type: str
    event_type: str
    target_resource: str
    provider: str
    execution_mode: str
    details: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class AutonomousOverviewResponse(BaseModel):
    autonomy_level: int
    execution_mode: str
    active_remediations_count: int
    total_plans_count: int
    completed_remediations_count: int
    success_rate_pct: float
    verification_success_rate_pct: float
    rollback_rate_pct: float
    blocked_actions_count: int
    incidents_prevented_est: int
    mode_indicator: str
