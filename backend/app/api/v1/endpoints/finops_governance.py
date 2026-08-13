"""
Enterprise FinOps Governance & Cost Control Center API endpoints.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_cost, crud_finops_governance
from app.models.user import User
from app.schemas.finops_governance import (
    CostPolicyCreate,
    CostPolicyListResponse,
    CostPolicyResponse,
    CostPolicyUpdate,
    CostViolationListResponse,
    CostViolationResponse,
    FinOpsAuditLogListResponse,
    FinOpsAuditLogResponse,
    GovernanceOverviewResponse,
    GovernanceScoreResponse,
    PolicyExceptionCreate,
    PolicyExceptionListResponse,
    PolicyExceptionResponse,
    PolicyExceptionStatusUpdate,
    RemediationActionListResponse,
    RemediationActionResponse,
    RemediationApprovePayload,
    RemediationExecutePayload,
    RemediationRequestPayload,
    ViolationStatusUpdate,
)
from app.services.finops_governance_engine import (
    calculate_finops_governance_score,
    evaluate_cost_policies,
    simulate_remediation_execution,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /finops/governance/score & /overview
# ---------------------------------------------------------------------------


@router.get(
    "/governance/score",
    response_model=GovernanceScoreResponse,
    summary="Get detailed deterministic FinOps Governance Score and compliance sub-scores",
)
async def get_governance_score(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceScoreResponse:
    policies, _ = await crud_finops_governance.get_policies(db, user_id=current_user.id, limit=300)
    violations, _ = await crud_finops_governance.get_violations(db, user_id=current_user.id, limit=300)
    overview_data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)

    score = calculate_finops_governance_score(
        policies=policies,
        violations=violations,
        potential_savings=overview_data["potential_savings"],
        total_spend=overview_data["monthly_cost"],
    )
    return GovernanceScoreResponse(**score)


@router.get(
    "/governance/overview",
    response_model=GovernanceOverviewResponse,
    summary="Get FinOps Governance overview metrics, score, violations, and remediation status",
)
async def get_governance_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceOverviewResponse:
    policies, total_pol = await crud_finops_governance.get_policies(db, user_id=current_user.id, limit=300)
    active_pol = sum(1 for p in policies if p.enabled)

    violations, total_viol = await crud_finops_governance.get_violations(db, user_id=current_user.id, limit=300)
    open_viol = sum(1 for v in violations if v.status == "OPEN")
    crit_viol = sum(1 for v in violations if v.status == "OPEN" and v.severity == "CRITICAL")

    exceptions = await crud_finops_governance.get_exceptions(db, user_id=current_user.id)
    active_exc = sum(1 for e in exceptions if e.status == "APPROVED" and e.expiration_date > datetime.now(UTC))

    remediations = await crud_finops_governance.get_remediations(db, user_id=current_user.id)
    pending_rem = sum(1 for r in remediations if r.approval_status in ("PENDING", "APPROVED"))
    savings_sum = sum(r.estimated_savings for r in remediations if r.approval_status != "EXECUTED")

    overview_cost = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)
    score = calculate_finops_governance_score(
        policies=policies,
        violations=violations,
        potential_savings=overview_cost["potential_savings"],
        total_spend=overview_cost["monthly_cost"],
    )

    return GovernanceOverviewResponse(
        governance_score=GovernanceScoreResponse(**score),
        total_policies=total_pol,
        active_policies=active_pol,
        open_violations=open_viol,
        critical_violations=crit_viol,
        active_exceptions=active_exc,
        pending_remediations=pending_rem,
        total_potential_savings=round(savings_sum, 2),
        mode_indicator="DEMO / LOCAL MODE — Controlled Remediations Simulated",
    )


# ---------------------------------------------------------------------------
# Policy CRUD (/finops/policies)
# ---------------------------------------------------------------------------


@router.get(
    "/policies",
    response_model=CostPolicyListResponse,
    summary="List FinOps cost policies with filters",
)
async def list_policies(
    provider: str | None = None,
    category: str | None = None,
    severity: str | None = None,
    enabled: bool | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostPolicyListResponse:
    items, total = await crud_finops_governance.get_policies(
        db,
        user_id=current_user.id,
        provider=provider,
        category=category,
        severity=severity,
        enabled=enabled,
        search=search,
        skip=skip,
        limit=limit,
    )
    return CostPolicyListResponse(
        policies=[CostPolicyResponse.model_validate(p) for p in items],
        total=total,
    )


@router.post(
    "/policies",
    response_model=CostPolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new FinOps cost policy",
)
async def create_policy(
    payload: CostPolicyCreate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostPolicyResponse:
    policy = await crud_finops_governance.create_policy(
        db,
        user_id=current_user.id,
        data=payload.model_dump(),
        actor_email=current_user.email,
    )
    return CostPolicyResponse.model_validate(policy)


@router.get(
    "/policies/{policy_id}",
    response_model=CostPolicyResponse,
    summary="Get single policy details by ID",
)
async def get_policy(
    policy_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostPolicyResponse:
    policy = await crud_finops_governance.get_policy_by_id(
        db, user_id=current_user.id, policy_id=policy_id
    )
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps cost policy not found",
        )
    return CostPolicyResponse.model_validate(policy)


@router.put(
    "/policies/{policy_id}",
    response_model=CostPolicyResponse,
    summary="Update existing cost policy parameters",
)
async def update_policy(
    policy_id: uuid.UUID,
    payload: CostPolicyUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostPolicyResponse:
    updated = await crud_finops_governance.update_policy(
        db,
        user_id=current_user.id,
        policy_id=policy_id,
        data=payload.model_dump(exclude_unset=True),
        actor_email=current_user.email,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps cost policy not found",
        )
    return CostPolicyResponse.model_validate(updated)


@router.patch(
    "/policies/{policy_id}/status",
    response_model=CostPolicyResponse,
    summary="Enable or disable a policy",
)
async def toggle_policy_status(
    policy_id: uuid.UUID,
    enabled: bool = Query(...),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostPolicyResponse:
    toggled = await crud_finops_governance.toggle_policy_status(
        db,
        user_id=current_user.id,
        policy_id=policy_id,
        enabled=enabled,
        actor_email=current_user.email,
    )
    if not toggled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps cost policy not found",
        )
    return CostPolicyResponse.model_validate(toggled)


@router.delete(
    "/policies/{policy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a cost policy",
)
async def delete_policy(
    policy_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    deleted = await crud_finops_governance.delete_policy(
        db, user_id=current_user.id, policy_id=policy_id, actor_email=current_user.email
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps cost policy not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/policies/{policy_id}/evaluate",
    summary="Trigger deterministic evaluation of cost policies",
)
async def evaluate_policies_endpoint(
    policy_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    res = await evaluate_cost_policies(db, user_id=current_user.id)
    await crud_finops_governance.create_audit_log(
        db,
        user_id=current_user.id,
        actor_email=current_user.email,
        action="POLICY_EVALUATED",
        entity_type="POLICY",
        entity_id=str(policy_id),
        metadata_json=res,
    )
    return res


# ---------------------------------------------------------------------------
# Violations (/finops/violations)
# ---------------------------------------------------------------------------


@router.get(
    "/violations",
    response_model=CostViolationListResponse,
    summary="List policy violations with severity and status filters",
)
async def list_violations(
    severity: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    provider: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostViolationListResponse:
    # Trigger auto evaluation on listing
    await evaluate_cost_policies(db, user_id=current_user.id)
    items, total = await crud_finops_governance.get_violations(
        db,
        user_id=current_user.id,
        severity=severity,
        status=status_filter,
        provider=provider,
        search=search,
        skip=skip,
        limit=limit,
    )

    crit = sum(1 for v in items if v.severity == "CRITICAL")
    high = sum(1 for v in items if v.severity == "HIGH")

    return CostViolationListResponse(
        violations=[CostViolationResponse.model_validate(v) for v in items],
        total=total,
        critical_count=crit,
        high_count=high,
    )


@router.get(
    "/violations/{violation_id}",
    response_model=CostViolationResponse,
    summary="Get single violation details",
)
async def get_violation(
    violation_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostViolationResponse:
    viol = await crud_finops_governance.get_violation_by_id(
        db, user_id=current_user.id, violation_id=violation_id
    )
    if not viol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps cost violation not found",
        )
    return CostViolationResponse.model_validate(viol)


@router.patch(
    "/violations/{violation_id}/status",
    response_model=CostViolationResponse,
    summary="Update violation status (OPEN, ACKNOWLEDGED, IN_REVIEW, RESOLVED, EXEMPTED)",
)
async def update_violation_status_endpoint(
    violation_id: uuid.UUID,
    payload: ViolationStatusUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostViolationResponse:
    updated = await crud_finops_governance.update_violation_status(
        db,
        user_id=current_user.id,
        violation_id=violation_id,
        status=payload.status,
        actor_email=current_user.email,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps cost violation not found",
        )
    return CostViolationResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# Exceptions (/finops/exceptions)
# ---------------------------------------------------------------------------


@router.get(
    "/exceptions",
    response_model=PolicyExceptionListResponse,
    summary="List policy exceptions and waivers",
)
async def list_exceptions(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PolicyExceptionListResponse:
    items = await crud_finops_governance.get_exceptions(db, user_id=current_user.id)
    return PolicyExceptionListResponse(
        exceptions=[PolicyExceptionResponse.model_validate(e) for e in items],
        total=len(items),
    )


@router.post(
    "/exceptions",
    response_model=PolicyExceptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a policy exception request",
)
async def create_exception(
    payload: PolicyExceptionCreate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PolicyExceptionResponse:
    policy = await crud_finops_governance.get_policy_by_id(
        db, user_id=current_user.id, policy_id=payload.policy_id
    )
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated policy not found",
        )

    exc = await crud_finops_governance.create_exception(
        db,
        user_id=current_user.id,
        data=payload.model_dump(),
        actor_email=current_user.email,
    )
    return PolicyExceptionResponse.model_validate(exc)


@router.patch(
    "/exceptions/{exception_id}",
    response_model=PolicyExceptionResponse,
    summary="Approve or reject a policy exception",
)
async def update_exception_status_endpoint(
    exception_id: uuid.UUID,
    payload: PolicyExceptionStatusUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PolicyExceptionResponse:
    updated = await crud_finops_governance.update_exception_status(
        db,
        user_id=current_user.id,
        exception_id=exception_id,
        status=payload.status,
        approved_by=payload.approved_by,
        actor_email=current_user.email,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy exception request not found",
        )
    return PolicyExceptionResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# Remediations (/finops/remediations)
# ---------------------------------------------------------------------------


@router.get(
    "/remediations",
    response_model=RemediationActionListResponse,
    summary="List controlled remediation queue actions",
)
async def list_remediations(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationActionListResponse:
    items = await crud_finops_governance.get_remediations(db, user_id=current_user.id)
    pending = sum(1 for r in items if r.approval_status in ("PENDING", "APPROVED"))
    savings = sum(r.estimated_savings for r in items if r.approval_status != "EXECUTED")

    return RemediationActionListResponse(
        remediations=[RemediationActionResponse.model_validate(r) for r in items],
        total=len(items),
        pending_approvals=pending,
        potential_savings=round(savings, 2),
    )


@router.post(
    "/remediations/request",
    response_model=RemediationActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request approval for a controlled remediation",
)
async def request_remediation(
    payload: RemediationRequestPayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationActionResponse:
    rem = await crud_finops_governance.request_remediation(
        db,
        user_id=current_user.id,
        data=payload.model_dump(),
        actor_email=current_user.email,
    )
    return RemediationActionResponse.model_validate(rem)


@router.post(
    "/remediations/{remediation_id}/approve",
    response_model=RemediationActionResponse,
    summary="Approve or reject a remediation request",
)
async def approve_remediation(
    remediation_id: uuid.UUID,
    payload: RemediationApprovePayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationActionResponse:
    rem = await crud_finops_governance.approve_remediation(
        db,
        user_id=current_user.id,
        remediation_id=remediation_id,
        status=payload.status,
        actor_email=current_user.email,
    )
    if not rem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation action not found",
        )
    return RemediationActionResponse.model_validate(rem)


@router.post(
    "/remediations/{remediation_id}/execute",
    response_model=RemediationActionResponse,
    summary="Execute approved remediation action (DRY_RUN or SIMULATED)",
)
async def execute_remediation(
    remediation_id: uuid.UUID,
    payload: RemediationExecutePayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationActionResponse:
    items = await crud_finops_governance.get_remediations(db, user_id=current_user.id)
    rem = next((r for r in items if r.id == remediation_id), None)
    if not rem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation action not found",
        )

    # Perform simulation execution
    sim = simulate_remediation_execution(
        action_type=rem.action_type,
        resource_name=rem.resource_name,
        provider=rem.provider,
        estimated_savings=rem.estimated_savings,
        execution_mode=payload.execution_mode,
    )

    rem.execution_mode = payload.execution_mode.upper()
    rem.approval_status = "EXECUTED"
    rem.executed_at = sim["executed_at"]
    rem.original_config = sim["original_config"]
    rem.recommended_config = sim["recommended_config"]
    rem.rollback_config = sim["rollback_config"]
    rem.execution_result = sim["result_message"]
    rem.updated_at = datetime.now(UTC)

    db.add(rem)
    await db.flush()

    await crud_finops_governance.create_audit_log(
        db,
        user_id=current_user.id,
        actor_email=current_user.email,
        action="REMEDIATION_EXECUTED",
        entity_type="REMEDIATION",
        entity_id=str(rem.id),
        metadata_json={
            "action_type": rem.action_type,
            "mode": rem.execution_mode,
            "result": rem.execution_result,
        },
    )

    return RemediationActionResponse.model_validate(rem)


@router.post(
    "/remediations/{remediation_id}/rollback",
    response_model=RemediationActionResponse,
    summary="Rollback executed remediation action",
)
async def rollback_remediation(
    remediation_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RemediationActionResponse:
    items = await crud_finops_governance.get_remediations(db, user_id=current_user.id)
    rem = next((r for r in items if r.id == remediation_id), None)
    if not rem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation action not found",
        )

    rem.approval_status = "ROLLED_BACK"
    rem.execution_result = (
        f"[SIMULATED ROLLBACK] Resource '{rem.resource_name}' state restored to original configuration. "
        f"Restored at {datetime.now(UTC).isoformat()}."
    )
    rem.updated_at = datetime.now(UTC)

    db.add(rem)
    await db.flush()

    await crud_finops_governance.create_audit_log(
        db,
        user_id=current_user.id,
        actor_email=current_user.email,
        action="REMEDIATION_ROLLED_BACK",
        entity_type="REMEDIATION",
        entity_id=str(rem.id),
        metadata_json={"action_type": rem.action_type, "result": rem.execution_result},
    )

    return RemediationActionResponse.model_validate(rem)


# ---------------------------------------------------------------------------
# Audit Trail (/finops/audit)
# ---------------------------------------------------------------------------


@router.get(
    "/audit",
    response_model=FinOpsAuditLogListResponse,
    summary="Get FinOps governance audit log activity",
)
async def get_audit_trail(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> FinOpsAuditLogListResponse:
    logs, total = await crud_finops_governance.get_audit_logs(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return FinOpsAuditLogListResponse(
        audit_logs=[FinOpsAuditLogResponse.model_validate(log_item) for log_item in logs],
        total=total,
    )
