"""
REST API Router for Enterprise AIOps Automated Remediation & Action Center.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud.crud_remediation import crud_remediation
from app.models.autonomous import RemediationApproval, RemediationAuditLog
from app.models.user import User
from app.schemas.remediation import (
    RemediationActionCreate,
    RemediationActionItem,
    RemediationAnalyzeResult,
    RemediationApprovalRequest,
    RemediationApprovalResponse,
    RemediationAuditResponse,
    RemediationDryRunRequest,
    RemediationDryRunResponse,
    RemediationExecuteRequest,
    RemediationExecutionResponse,
    RemediationOverviewResponse,
    RemediationPlanResponse,
    RemediationPolicyCreate,
    RemediationPolicyResponse,
    RemediationPolicyUpdate,
    RemediationRejectionRequest,
)
from app.services.autonomous import action_catalog
from app.services.remediation_engine import (
    analyze_remediation_ai,
    classify_action_risk,
    execute_remediation_dry_run,
    execute_remediation_simulation,
    execute_rollback,
    validate_state_transition,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# ── 1. GET /remediation/overview ─────────────────────────────────────────────


@router.get(
    "/overview",
    response_model=RemediationOverviewResponse,
    summary="Get AIOps Action Center overview metrics",
)
async def get_remediation_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationOverviewResponse:
    plans = await crud_remediation.get_plans(db, limit=200)
    executions = await crud_remediation.get_executions(db, limit=200)
    policies = await crud_remediation.get_policies(db)

    pending_approvals = [p for p in plans if p.status in ("PLANNED", "AWAITING_APPROVAL", "RECOMMENDED")]
    active_execs = [e for e in executions if e.status in ("QUEUED", "VALIDATING", "EXECUTING", "VERIFYING")]
    completed_execs = [e for e in executions if e.status in ("COMPLETED", "SUCCEEDED")]
    failed_execs = [e for e in executions if e.status == "FAILED"]
    rollback_available = [e for e in executions if e.rollback_status == "ROLLBACK_AVAILABLE"]

    total_finished = len(completed_execs) + len(failed_execs)
    success_rate = round((len(completed_execs) / total_finished) * 100, 1) if total_finished > 0 else 98.5

    return RemediationOverviewResponse(
        pending_approvals_count=len(pending_approvals),
        active_executions_count=len(active_execs),
        completed_remediations_count=len(completed_execs),
        failed_remediations_count=len(failed_execs),
        rollback_available_count=len(rollback_available),
        success_rate_pct=success_rate,
        automation_policy_count=len(policies),
        cooldown_active_count=1 if len(active_execs) > 0 else 0,
        mode_indicator="DEMO / LOCAL SIMULATION MODE — Infrastructure Credentials Simulated",
    )


# ── 2. GET /remediation/actions & GET /remediation/actions/{id} ───────────────


@router.get(
    "/actions",
    response_model=list[RemediationPlanResponse],
    summary="List remediation action plans",
)
async def list_remediation_actions(
    status: str | None = Query(default=None),
    provider: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationPlanResponse]:
    status_filter = status if isinstance(status, str) else None
    provider_filter = provider if isinstance(provider, str) else None
    risk_filter = risk_level if isinstance(risk_level, str) else None
    plans = await crud_remediation.get_plans(
        db, user_id=current_user.id, status=status_filter, provider=provider_filter, risk_level=risk_filter
    )
    if not plans:
        # Seed initial realistic remediation plans if empty
        p1 = await crud_remediation.create_plan(
            db,
            user_id=current_user.id,
            trigger_source="incident_intelligence",
            source_event_id="INC-8942",
            root_cause="Elevated error rate (5.2%) on payment-service downstream dependency.",
            affected_resource="payment-service",
            provider="AWS",
            environment="production",
            action_type="SERVICE_RESTART",
            risk_level="MEDIUM",
            expected_impact="Restore service health to 99.9% availability.",
            estimated_downtime_sec=15,
            estimated_cost_impact=0.0,
            requires_approval=True,
            rollback_supported=True,
            execution_mode="SIMULATION",
            status="AWAITING_APPROVAL",
        )
        p2 = await crud_remediation.create_plan(
            db,
            user_id=current_user.id,
            trigger_source="capacity_risk",
            source_event_id="CAP-104",
            root_cause="Kubernetes order-processor deployment CPU utilization > 88%.",
            affected_resource="order-processor",
            provider="Kubernetes",
            environment="production",
            action_type="SCALE_UP",
            risk_level="MEDIUM",
            expected_impact="Scale deployment replicas from 3 to 5 to eliminate latency bottleneck.",
            estimated_downtime_sec=0,
            estimated_cost_impact=45.0,
            requires_approval=True,
            rollback_supported=True,
            execution_mode="SIMULATION",
            status="RECOMMENDED",
        )
        plans = [p1, p2]

    return [RemediationPlanResponse.model_validate(p) for p in plans]


@router.get(
    "/actions/definitions",
    response_model=list[RemediationActionItem],
    summary="List available remediation action definitions from catalog",
)
async def list_action_definitions(
    current_user: User = Depends(require_active_user),
) -> list[RemediationActionItem]:
    defs = action_catalog.list_action_definitions()
    return [RemediationActionItem(**d) for d in defs]


@router.get(
    "/actions/{plan_id}",
    response_model=RemediationPlanResponse,
    summary="Get single remediation plan detail",
)
async def get_remediation_action_detail(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPlanResponse:
    plan = await crud_remediation.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Remediation plan {plan_id} not found.")
    return RemediationPlanResponse.model_validate(plan)


# ── 3. POST /remediation/actions ──────────────────────────────────────────────


@router.post(
    "/actions",
    response_model=RemediationPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new remediation action plan",
)
async def create_remediation_action(
    action_in: RemediationActionCreate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPlanResponse:
    risk = classify_action_risk(action_in.action_type, action_in.environment)
    requires_approval = risk in ("MEDIUM", "HIGH", "CRITICAL")
    init_status = "AWAITING_APPROVAL" if requires_approval else "RECOMMENDED"

    plan = await crud_remediation.create_plan(
        db,
        user_id=current_user.id,
        trigger_source=action_in.trigger_source,
        source_event_id=action_in.source_event_id,
        root_cause=action_in.root_cause,
        affected_resource=action_in.affected_resource,
        provider=action_in.provider,
        environment=action_in.environment,
        action_type=action_in.action_type,
        risk_level=risk,
        expected_impact=action_in.expected_impact,
        estimated_downtime_sec=action_in.estimated_downtime_sec,
        estimated_cost_impact=action_in.estimated_cost_impact,
        requires_approval=requires_approval,
        rollback_supported=True,
        execution_mode=action_in.execution_mode,
        status=init_status,
    )
    return RemediationPlanResponse.model_validate(plan)


# ── 4. POST /remediation/actions/{id}/dry-run ─────────────────────────────────


@router.post(
    "/actions/{plan_id}/dry-run",
    response_model=RemediationDryRunResponse,
    summary="Execute dry-run for a remediation plan",
)
async def dry_run_remediation_action(
    plan_id: uuid.UUID,
    req: RemediationDryRunRequest | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationDryRunResponse:
    plan = await crud_remediation.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Remediation plan {plan_id} not found.")

    res = await execute_remediation_dry_run(db, plan)
    return RemediationDryRunResponse(**res)


# ── 5. POST /remediation/actions/{id}/approve & /reject ───────────────────────


@router.post(
    "/actions/{plan_id}/approve",
    response_model=RemediationApprovalResponse,
    summary="Approve a pending remediation plan",
)
async def approve_remediation_action(
    plan_id: uuid.UUID,
    req: RemediationApprovalRequest | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationApprovalResponse:
    plan = await crud_remediation.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Remediation plan {plan_id} not found.")

    if not validate_state_transition(plan.status, "APPROVED"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state transition: Cannot approve plan in '{plan.status}' status.",
        )

    # Check RBAC: Self-approval prohibited for CRITICAL actions if user is creator
    if plan.risk_level.upper() == "CRITICAL" and plan.user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="RBAC Policy Violation: Multi-user approval required for CRITICAL risk actions. Creator cannot self-approve.",
        )

    plan.status = "APPROVED"
    approval = RemediationApproval(
        plan_id=plan.id,
        approver_id=current_user.id,
        approver_role="Admin",
        approval_status="APPROVED",
        comments=req.comments if req else "Approved via AIOps Action Center.",
    )
    db.add(approval)

    audit = RemediationAuditLog(
        plan_id=plan.id,
        actor_id=current_user.id,
        action_type=plan.action_type,
        event_type="APPROVED",
        target_resource=plan.affected_resource,
        provider=plan.provider,
        execution_mode=plan.execution_mode,
        details={"status": "APPROVED", "comments": approval.comments},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(approval)

    return RemediationApprovalResponse.model_validate(approval)


@router.post(
    "/actions/{plan_id}/reject",
    response_model=RemediationApprovalResponse,
    summary="Reject a pending remediation plan",
)
async def reject_remediation_action(
    plan_id: uuid.UUID,
    req: RemediationRejectionRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationApprovalResponse:
    plan = await crud_remediation.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Remediation plan {plan_id} not found.")

    plan.status = "REJECTED"
    approval = RemediationApproval(
        plan_id=plan.id,
        approver_id=current_user.id,
        approver_role="Admin",
        approval_status="REJECTED",
        comments=req.rejection_reason,
    )
    db.add(approval)

    audit = RemediationAuditLog(
        plan_id=plan.id,
        actor_id=current_user.id,
        action_type=plan.action_type,
        event_type="REJECTED",
        target_resource=plan.affected_resource,
        provider=plan.provider,
        execution_mode=plan.execution_mode,
        details={"status": "REJECTED", "reason": req.rejection_reason},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(approval)

    return RemediationApprovalResponse.model_validate(approval)


# ── 6. POST /remediation/actions/{id}/execute ─────────────────────────────────


@router.post(
    "/actions/{plan_id}/execute",
    response_model=dict[str, Any],
    summary="Execute an approved remediation plan",
)
async def execute_remediation_action(
    plan_id: uuid.UUID,
    req: RemediationExecuteRequest | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    plan = await crud_remediation.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Remediation plan {plan_id} not found.")

    mode = req.execution_mode if req and req.execution_mode else plan.execution_mode
    ik = req.idempotency_key if req and req.idempotency_key else f"exec-{plan_id}-{uuid.uuid4().hex[:8]}"

    res = await execute_remediation_simulation(
        db, plan=plan, user=current_user, idempotency_key=ik, execution_mode=mode
    )
    return res


# ── 7. POST /remediation/actions/{id}/rollback ────────────────────────────────


@router.post(
    "/actions/{execution_id}/rollback",
    response_model=dict[str, Any],
    summary="Rollback a completed or failed remediation execution",
)
async def rollback_remediation_action(
    execution_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    res = await execute_rollback(db, execution_id=execution_id, user=current_user)
    return res


# ── 8. GET /remediation/executions & /executions/{id} ─────────────────────────


@router.get(
    "/executions",
    response_model=list[RemediationExecutionResponse],
    summary="List remediation execution records",
)
async def list_remediation_executions(
    plan_id: uuid.UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationExecutionResponse]:
    execs = await crud_remediation.get_executions(db, plan_id=plan_id, status=status)
    return [RemediationExecutionResponse.model_validate(e) for e in execs]


@router.get(
    "/executions/{execution_id}",
    response_model=RemediationExecutionResponse,
    summary="Get single remediation execution detail",
)
async def get_remediation_execution_detail(
    execution_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationExecutionResponse:
    exc = await crud_remediation.get_execution(db, execution_id)
    if not exc:
        raise HTTPException(status_code=404, detail=f"Execution ID {execution_id} not found.")
    return RemediationExecutionResponse.model_validate(exc)


# ── 9. GET & POST & PUT /remediation/policies ─────────────────────────────────


@router.get(
    "/policies",
    response_model=list[RemediationPolicyResponse],
    summary="List remediation policies",
)
async def list_remediation_policies(
    is_enabled: bool | None = Query(default=None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationPolicyResponse]:
    policies = await crud_remediation.get_policies(db, is_enabled=is_enabled)
    if not policies:
        # Seed default policy
        pol = await crud_remediation.create_policy(
            db,
            policy_in=RemediationPolicyCreate(
                name="Default Auto-Service Restart Policy",
                trigger_signal="INCIDENT",
                condition_logic={"error_rate_pct": 3.0},
                action_type="SERVICE_RESTART",
                risk_level="MEDIUM",
                execution_mode="APPROVED",
                cooldown_minutes=5,
                is_enabled=True,
            ),
            created_by=current_user.email,
        )
        policies = [pol]

    return [RemediationPolicyResponse.model_validate(p) for p in policies]


@router.post(
    "/policies",
    response_model=RemediationPolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new remediation policy",
)
async def create_remediation_policy(
    policy_in: RemediationPolicyCreate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPolicyResponse:
    pol = await crud_remediation.create_policy(db, policy_in=policy_in, created_by=current_user.email)
    return RemediationPolicyResponse.model_validate(pol)


@router.put(
    "/policies/{policy_id}",
    response_model=RemediationPolicyResponse,
    summary="Update a remediation policy",
)
async def update_remediation_policy(
    policy_id: uuid.UUID,
    policy_in: RemediationPolicyUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationPolicyResponse:
    pol = await crud_remediation.get_policy(db, policy_id)
    if not pol:
        raise HTTPException(status_code=404, detail=f"Policy ID {policy_id} not found.")

    updated_pol = await crud_remediation.update_policy(db, policy=pol, policy_in=policy_in)
    return RemediationPolicyResponse.model_validate(updated_pol)


# ── 10. GET /remediation/audit ────────────────────────────────────────────────


@router.get(
    "/audit",
    response_model=list[RemediationAuditResponse],
    summary="Get remediation audit log trail",
)
async def get_remediation_audit_trail(
    plan_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RemediationAuditResponse]:
    logs = await crud_remediation.get_audit_logs(db, plan_id=plan_id)
    return [RemediationAuditResponse.model_validate(log_item) for log_item in logs]


# ── 11. POST /remediation/analyze ─────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=RemediationAnalyzeResult,
    summary="Trigger AI or Local Remediation Intelligence Brief",
)
async def analyze_remediation(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationAnalyzeResult:
    res = await analyze_remediation_ai(db, user_id=current_user.id)
    return RemediationAnalyzeResult(**res)
