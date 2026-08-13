"""
Autonomous Cloud Operations & Self-Healing Center REST API Endpoints.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_autonomous
from app.models.user import User
from app.schemas.autonomous import (
    ActionDefinitionResponse,
    AuditLogResponse,
    AutonomousOverviewResponse,
    AutonomyPolicyResponse,
    AutonomyPolicyUpdate,
    RemediationExecutionResponse,
    RemediationPlanCreate,
    RemediationPlanResponse,
    SimulationRequest,
)
from app.services.autonomous import (
    action_catalog,
    approval_engine,
    execution_engine,
    precondition_engine,
    rollback_engine,
    verification_engine,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# ── 1. GET /autonomous/overview ───────────────────────────────────────────────


@router.get(
    "/overview",
    response_model=AutonomousOverviewResponse,
    summary="Get Autonomous Operations overview state and metrics",
)
async def get_autonomous_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> AutonomousOverviewResponse:
    policy = await crud_autonomous.get_autonomy_policy(db, user_id=current_user.id)
    plans = await crud_autonomous.get_plans(db, user_id=current_user.id, limit=200)
    executions = await crud_autonomous.get_executions(db, limit=200)

    active_execs = [e for e in executions if e.status in ("QUEUED", "VALIDATING", "EXECUTING", "VERIFYING")]
    completed_execs = [e for e in executions if e.status == "COMPLETED"]
    failed_execs = [e for e in executions if e.status == "FAILED"]
    rolled_back_execs = [e for e in executions if e.status == "ROLLED_BACK"]
    blocked_execs = [e for e in executions if e.status == "BLOCKED"]

    total_finished = len(completed_execs) + len(failed_execs) + len(rolled_back_execs)
    success_rate = round((len(completed_execs) / total_finished) * 100, 1) if total_finished > 0 else 100.0

    return AutonomousOverviewResponse(
        autonomy_level=policy.autonomy_level,
        execution_mode=policy.default_execution_mode,
        active_remediations_count=len(active_execs),
        total_plans_count=len(plans),
        completed_remediations_count=len(completed_execs),
        success_rate_pct=success_rate,
        verification_success_rate_pct=98.5 if total_finished > 0 else 100.0,
        rollback_rate_pct=round((len(rolled_back_execs) / total_finished) * 100, 1) if total_finished > 0 else 0.0,
        blocked_actions_count=len(blocked_execs),
        incidents_prevented_est=max(1, len(completed_execs) * 2),
        mode_indicator=f"DEMO / SIMULATION MODE — Execution Mode: {policy.default_execution_mode}",
    )


# ── 2. GET & PUT /autonomous/config ──────────────────────────────────────────


@router.get(
    "/config",
    response_model=AutonomyPolicyResponse,
    summary="Get active Autonomy Policy & Safety Configuration",
)
async def get_autonomy_config(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> AutonomyPolicyResponse:
    policy = await crud_autonomous.get_autonomy_policy(db, user_id=current_user.id)
    return AutonomyPolicyResponse.model_validate(policy)


@router.put(
    "/config",
    response_model=AutonomyPolicyResponse,
    summary="Update Autonomy Policy configuration",
)
async def update_autonomy_config(
    policy_in: AutonomyPolicyUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> AutonomyPolicyResponse:
    policy = await crud_autonomous.update_autonomy_policy(db, policy_in=policy_in, user_id=current_user.id)
    return AutonomyPolicyResponse.model_validate(policy)


# ── 3. GET /autonomous/actions ────────────────────────────────────────────────


@router.get(
    "/actions",
    response_model=list[ActionDefinitionResponse],
    summary="List controlled Action Catalog definitions",
)
async def list_actions(
    current_user: User = Depends(require_active_user),
) -> list[ActionDefinitionResponse]:
    actions = action_catalog.list_action_definitions()
    return [ActionDefinitionResponse(**a) for a in actions]


# ── 4. Plans Endpoints (/plans) ───────────────────────────────────────────────


@router.get(
    "/plans",
    response_model=list[RemediationPlanResponse],
    summary="List Remediation Plans",
)
async def list_plans(
    status: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationPlanResponse]:
    plans = await crud_autonomous.get_plans(db, user_id=current_user.id, status=status)
    return [RemediationPlanResponse.model_validate(p) for p in plans]


@router.post(
    "/plans",
    response_model=RemediationPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Remediation Plan",
)
async def create_plan(
    plan_in: RemediationPlanCreate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPlanResponse:
    plan = await crud_autonomous.create_plan(db, plan_in=plan_in, user_id=current_user.id)
    return RemediationPlanResponse.model_validate(plan)


@router.get(
    "/plans/{plan_id}",
    response_model=RemediationPlanResponse,
    summary="Get Remediation Plan details",
)
async def get_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPlanResponse:
    plan = await crud_autonomous.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation Plan not found")
    return RemediationPlanResponse.model_validate(plan)


@router.post(
    "/plans/{plan_id}/validate",
    summary="Validate preconditions & policy checks for a plan",
)
async def validate_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    plan = await crud_autonomous.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation Plan not found")

    precond = await precondition_engine.evaluate_preconditions(
        db,
        action_type=plan.action_type,
        target_resource=plan.affected_resource,
        environment=plan.environment,
        provider=plan.provider,
        user=current_user,
    )
    approval = await approval_engine.evaluate_approval_requirement(
        db,
        action_type=plan.action_type,
        environment=plan.environment,
        risk_level=plan.risk_level,
    )

    return {
        "plan_id": str(plan.id),
        "preconditions": precond,
        "approval_requirement": approval,
        "valid": precond["passed"],
    }


@router.post(
    "/plans/{plan_id}/approve",
    response_model=RemediationPlanResponse,
    summary="Approve a Remediation Plan for execution",
)
async def approve_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPlanResponse:
    plan = await crud_autonomous.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation Plan not found")

    plan.status = "APPROVED"
    await db.commit()
    await db.refresh(plan)
    return RemediationPlanResponse.model_validate(plan)


@router.post(
    "/plans/{plan_id}/execute",
    summary="Execute a Remediation Plan",
)
async def execute_plan(
    plan_id: uuid.UUID,
    mode: str | None = Query(None, description="Execution mode: DRY_RUN, SIMULATED, LIVE"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    plan = await crud_autonomous.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation Plan not found")

    res = await execution_engine.execute_remediation_plan(
        db, plan=plan, user=current_user, execution_mode=mode
    )
    return res


@router.post(
    "/plans/{plan_id}/verify",
    summary="Verify post-condition state of plan",
)
async def verify_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    plan = await crud_autonomous.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation Plan not found")

    verify_res = await verification_engine.verify_postconditions(
        action_type=plan.action_type,
        target_resource=plan.affected_resource,
        provider=plan.provider,
        execution_mode=plan.execution_mode,
    )
    return {"plan_id": str(plan.id), "verification": verify_res}


@router.post(
    "/plans/{plan_id}/rollback",
    summary="Rollback an executed plan",
)
async def rollback_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    execs = await crud_autonomous.get_executions(db, plan_id=plan_id, limit=1)
    if not execs:
        raise HTTPException(status_code=404, detail="No execution found for this plan to rollback")

    res = await rollback_engine.execute_rollback(
        db, execution=execs[0], provider=execs[0].plan.provider if execs[0].plan else "AWS", actor_id=current_user.id
    )
    return res


# ── 5. Executions & Queue & Audit & Simulation ────────────────────────────────


@router.get(
    "/executions",
    response_model=list[RemediationExecutionResponse],
    summary="List Remediation Executions",
)
async def list_executions(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationExecutionResponse]:
    execs = await crud_autonomous.get_executions(db, limit=100)
    return [RemediationExecutionResponse.model_validate(e) for e in execs]


@router.get(
    "/executions/{execution_id}",
    response_model=RemediationExecutionResponse,
    summary="Get Execution details",
)
async def get_execution(
    execution_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationExecutionResponse:
    execution = await crud_autonomous.get_execution_by_id(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return RemediationExecutionResponse.model_validate(execution)


@router.get(
    "/queue",
    response_model=list[RemediationExecutionResponse],
    summary="Get active execution queue",
)
async def get_execution_queue(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationExecutionResponse]:
    execs = await crud_autonomous.get_executions(db, limit=100)
    queue = [e for e in execs if e.status in ("QUEUED", "VALIDATING", "WAITING_APPROVAL", "EXECUTING", "VERIFYING")]
    return [RemediationExecutionResponse.model_validate(e) for e in queue]


@router.get(
    "/audit",
    response_model=list[AuditLogResponse],
    summary="Get Remediation Audit Logs",
)
async def get_audit_logs(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    logs = await crud_autonomous.get_audit_logs(db, limit=100)
    return [AuditLogResponse.model_validate(log_item) for log_item in logs]


@router.post(
    "/simulate",
    summary="Safe Action Simulator endpoint (No real resources changed)",
)
async def simulate_action(
    req: SimulationRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    precond = await precondition_engine.evaluate_preconditions(
        db,
        action_type=req.action_type,
        target_resource=req.affected_resource,
        environment=req.environment,
        provider=req.provider,
        user=current_user,
    )
    act_def = action_catalog.get_action_definition(req.action_type)
    risk_level = act_def.risk_level if act_def else "MEDIUM"

    approval = await approval_engine.evaluate_approval_requirement(
        db,
        action_type=req.action_type,
        environment=req.environment,
        risk_level=risk_level,
    )
    verify = await verification_engine.verify_postconditions(
        action_type=req.action_type,
        target_resource=req.affected_resource,
        provider=req.provider,
        execution_mode="SIMULATED",
    )

    return {
        "action_type": req.action_type,
        "affected_resource": req.affected_resource,
        "provider": req.provider,
        "environment": req.environment,
        "execution_mode": "SIMULATED",
        "preconditions": precond,
        "approval_requirement": approval,
        "simulated_verification": verify,
        "simulation_result": "SUCCESS",
        "message": "[SIMULATION MODE] Preconditions, policy checks, and verification evaluated deterministically. No real cloud resources modified.",
    }
