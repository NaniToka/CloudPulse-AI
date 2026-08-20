"""
CRUD operations for FinOps Governance models:
- Policies
- Violations
- Exceptions
- Remediations
- Audit Logs
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finops_governance import (
    FinOpsCostPolicy,
    FinOpsCostViolation,
    FinOpsGovernanceAuditLog,
    FinOpsPolicyException,
    FinOpsRemediationAction,
)

# ── Default Policy Seeding ───────────────────────────────────────────────────


async def seed_default_policies_if_empty(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Seed sample FinOps cost policies if user has no policies configured."""
    count_stmt = select(func.count()).select_from(FinOpsCostPolicy).where(
        FinOpsCostPolicy.user_id == user_id
    )
    res = await db.execute(count_stmt)
    if res.scalar_one() > 0:
        return

    now = datetime.now(UTC)
    sample_policies = [
        (
            "AWS Production Compute Monthly Cap",
            "AWS EC2 and compute spend in production environment must not exceed $15,000/month.",
            "SPENDING",
            "aws",
            "production",
            "monthly_spend",
            ">",
            15000.0,
            "HIGH",
            True,
        ),
        (
            "Max Single Compute Instance Cost Limit",
            "Any single cloud compute instance exceeding $3,500/month must trigger a rightsizing review.",
            "RESOURCE",
            "all",
            "all",
            "resource_cost",
            ">",
            3500.0,
            "CRITICAL",
            True,
        ),
        (
            "Idle Cloud Compute Waste Threshold",
            "Total idle resource waste must remain below $2,500/month across all cloud providers.",
            "WASTE",
            "all",
            "all",
            "waste_cost",
            ">",
            2500.0,
            "HIGH",
            True,
        ),
        (
            "GCP Infrastructure Budget Utilization Cap",
            "GCP cloud infrastructure spend must not breach 90% of allocated department budget.",
            "BUDGET",
            "gcp",
            "production",
            "budget_utilization",
            ">",
            90.0,
            "CRITICAL",
            True,
        ),
        (
            "Cost Anomaly Spike Severity Guardrail",
            "Any detected cloud spending spike with anomaly score >= 7.5 triggers immediate policy review.",
            "ANOMALY",
            "all",
            "all",
            "anomaly_score",
            ">=",
            7.5,
            "HIGH",
            True,
        ),
        (
            "Kubernetes Workload Spend Ceiling",
            "Kubernetes cluster node compute spend must not exceed $10,000/month.",
            "KUBERNETES",
            "kubernetes",
            "production",
            "monthly_spend",
            ">",
            10000.0,
            "MEDIUM",
            True,
        ),
    ]

    for (
        name,
        desc,
        cat,
        prov,
        scope,
        metric,
        op,
        thresh,
        sev,
        enabled,
    ) in sample_policies:
        pol = FinOpsCostPolicy(
            id=uuid.uuid4(),
            name=name,
            description=desc,
            category=cat,
            provider=prov,
            scope=scope,
            metric=metric,
            operator=op,
            threshold_value=thresh,
            severity=sev,
            enabled=enabled,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        db.add(pol)

    await db.flush()


# ── Audit Log CRUD ────────────────────────────────────────────────────────────


async def create_audit_log(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    actor_email: str,
    action: str,
    entity_type: str,
    entity_id: str,
    result: str = "SUCCESS",
    metadata_json: dict[str, Any] | None = None,
) -> FinOpsGovernanceAuditLog:
    """Record an immutable governance audit log entry."""
    entry = FinOpsGovernanceAuditLog(
        id=uuid.uuid4(),
        user_id=user_id,
        actor_email=actor_email,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        result=result,
        metadata_json=metadata_json or {},
        timestamp=datetime.now(UTC),
    )
    db.add(entry)
    await db.flush()
    return entry


async def get_audit_logs(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[FinOpsGovernanceAuditLog], int]:
    """Fetch paginated audit log activity."""
    stmt = (
        select(FinOpsGovernanceAuditLog)
        .where(FinOpsGovernanceAuditLog.user_id == user_id)
        .order_by(FinOpsGovernanceAuditLog.timestamp.desc())
    )
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    res = await db.execute(stmt.offset(skip).limit(limit))
    return list(res.scalars().all()), total


# ── Policy CRUD ───────────────────────────────────────────────────────────────


async def get_policies(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: str | None = None,
    category: str | None = None,
    severity: str | None = None,
    enabled: bool | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[FinOpsCostPolicy], int]:
    """Fetch paginated & filtered cost policies."""
    await seed_default_policies_if_empty(db, user_id)

    stmt = select(FinOpsCostPolicy).where(FinOpsCostPolicy.user_id == user_id)
    if provider and provider != "all":
        stmt = stmt.where(FinOpsCostPolicy.provider == provider)
    if category:
        stmt = stmt.where(FinOpsCostPolicy.category == category)
    if severity:
        stmt = stmt.where(FinOpsCostPolicy.severity == severity.upper())
    if enabled is not None:
        stmt = stmt.where(FinOpsCostPolicy.enabled.is_(enabled))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            FinOpsCostPolicy.name.ilike(pattern)
            | FinOpsCostPolicy.description.ilike(pattern)
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    stmt = stmt.order_by(FinOpsCostPolicy.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all()), total


async def get_policy_by_id(
    db: AsyncSession, *, user_id: uuid.UUID, policy_id: uuid.UUID
) -> FinOpsCostPolicy | None:
    """Fetch single cost policy by ID."""
    stmt = select(FinOpsCostPolicy).where(
        FinOpsCostPolicy.id == policy_id, FinOpsCostPolicy.user_id == user_id
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_policy(
    db: AsyncSession, *, user_id: uuid.UUID, data: dict[str, Any], actor_email: str
) -> FinOpsCostPolicy:
    """Create a new FinOps cost policy."""
    policy = FinOpsCostPolicy(
        id=uuid.uuid4(),
        user_id=user_id,
        name=data["name"],
        description=data.get("description"),
        category=data.get("category", "SPENDING"),
        provider=data.get("provider", "all"),
        scope=data.get("scope", "all"),
        metric=data["metric"],
        operator=data.get("operator", ">"),
        threshold_value=float(data["threshold_value"]),
        severity=data.get("severity", "MEDIUM").upper(),
        enabled=data.get("enabled", True),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(policy)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="POLICY_CREATED",
        entity_type="POLICY",
        entity_id=str(policy.id),
        metadata_json={"policy_name": policy.name, "threshold": policy.threshold_value},
    )

    return policy


async def update_policy(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    policy_id: uuid.UUID,
    data: dict[str, Any],
    actor_email: str,
) -> FinOpsCostPolicy | None:
    """Update existing cost policy parameters."""
    policy = await get_policy_by_id(db, user_id=user_id, policy_id=policy_id)
    if not policy:
        return None

    for key, val in data.items():
        if val is not None and hasattr(policy, key):
            setattr(policy, key, val)

    policy.updated_at = datetime.now(UTC)
    db.add(policy)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="POLICY_UPDATED",
        entity_type="POLICY",
        entity_id=str(policy.id),
        metadata_json={"policy_name": policy.name},
    )

    return policy


async def toggle_policy_status(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    policy_id: uuid.UUID,
    enabled: bool,
    actor_email: str,
) -> FinOpsCostPolicy | None:
    """Enable or disable a policy."""
    policy = await get_policy_by_id(db, user_id=user_id, policy_id=policy_id)
    if not policy:
        return None

    policy.enabled = enabled
    policy.updated_at = datetime.now(UTC)
    db.add(policy)
    await db.flush()

    act = "POLICY_ENABLED" if enabled else "POLICY_DISABLED"
    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action=act,
        entity_type="POLICY",
        entity_id=str(policy.id),
        metadata_json={"policy_name": policy.name, "enabled": enabled},
    )

    return policy


async def delete_policy(
    db: AsyncSession, *, user_id: uuid.UUID, policy_id: uuid.UUID, actor_email: str
) -> bool:
    """Delete a cost policy."""
    policy = await get_policy_by_id(db, user_id=user_id, policy_id=policy_id)
    if not policy:
        return False

    policy_name = policy.name
    await db.delete(policy)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="POLICY_DELETED",
        entity_type="POLICY",
        entity_id=str(policy_id),
        metadata_json={"policy_name": policy_name},
    )

    return True


# ── Violation CRUD ────────────────────────────────────────────────────────────


async def get_violations(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    severity: str | None = None,
    status: str | None = None,
    provider: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[FinOpsCostViolation], int]:
    """Fetch cost violations."""
    stmt = select(FinOpsCostViolation).where(FinOpsCostViolation.user_id == user_id)
    if severity:
        stmt = stmt.where(FinOpsCostViolation.severity == severity.upper())
    if status:
        stmt = stmt.where(FinOpsCostViolation.status == status.upper())
    if provider and provider != "all":
        stmt = stmt.where(FinOpsCostViolation.provider == provider)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            FinOpsCostViolation.policy_name.ilike(pattern)
            | FinOpsCostViolation.resource_name.ilike(pattern)
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    stmt = stmt.order_by(FinOpsCostViolation.detected_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all()), total


async def get_violation_by_id(
    db: AsyncSession, *, user_id: uuid.UUID, violation_id: uuid.UUID
) -> FinOpsCostViolation | None:
    """Fetch single violation by ID."""
    stmt = select(FinOpsCostViolation).where(
        FinOpsCostViolation.id == violation_id, FinOpsCostViolation.user_id == user_id
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def update_violation_status(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    violation_id: uuid.UUID,
    status: str,
    actor_email: str,
) -> FinOpsCostViolation | None:
    """Update violation status (OPEN, ACKNOWLEDGED, IN_REVIEW, RESOLVED, EXEMPTED)."""
    viol = await get_violation_by_id(db, user_id=user_id, violation_id=violation_id)
    if not viol:
        return None

    viol.status = status.upper()
    viol.updated_at = datetime.now(UTC)
    db.add(viol)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="VIOLATION_UPDATED",
        entity_type="VIOLATION",
        entity_id=str(viol.id),
        metadata_json={"policy_name": viol.policy_name, "new_status": viol.status},
    )

    return viol


# ── Exception CRUD ────────────────────────────────────────────────────────────


async def get_exceptions(
    db: AsyncSession, *, user_id: uuid.UUID
) -> list[FinOpsPolicyException]:
    """Fetch policy exceptions for user."""
    stmt = (
        select(FinOpsPolicyException)
        .where(FinOpsPolicyException.user_id == user_id)
        .order_by(FinOpsPolicyException.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def create_exception(
    db: AsyncSession, *, user_id: uuid.UUID, data: dict[str, Any], actor_email: str
) -> FinOpsPolicyException:
    """Create a policy exception request."""
    exc = FinOpsPolicyException(
        id=uuid.uuid4(),
        user_id=user_id,
        policy_id=uuid.UUID(str(data["policy_id"])),
        scope=data.get("scope", "all"),
        reason=data["reason"],
        requested_by=actor_email,
        status="PENDING",
        expiration_date=data["expiration_date"],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(exc)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="EXCEPTION_CREATED",
        entity_type="EXCEPTION",
        entity_id=str(exc.id),
        metadata_json={"policy_id": str(exc.policy_id), "reason": exc.reason},
    )

    return exc


async def update_exception_status(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    exception_id: uuid.UUID,
    status: str,
    approved_by: str | None = None,
    actor_email: str,
) -> FinOpsPolicyException | None:
    """Approve or reject a policy exception."""
    stmt = select(FinOpsPolicyException).where(
        FinOpsPolicyException.id == exception_id, FinOpsPolicyException.user_id == user_id
    )
    res = await db.execute(stmt)
    exc = res.scalar_one_or_none()
    if not exc:
        return None

    exc.status = status.upper()
    if approved_by:
        exc.approved_by = approved_by
    elif status.upper() == "APPROVED":
        exc.approved_by = actor_email

    exc.updated_at = datetime.now(UTC)
    db.add(exc)

    # If exception approved, update corresponding policy violations status to EXEMPTED
    if exc.status == "APPROVED":
        viol_stmt = (
            update(FinOpsCostViolation)
            .where(
                FinOpsCostViolation.policy_id == exc.policy_id,
                FinOpsCostViolation.user_id == user_id,
                FinOpsCostViolation.status == "OPEN",
            )
            .values(status="EXEMPTED", updated_at=datetime.now(UTC))
        )
        await db.execute(viol_stmt)

    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="EXCEPTION_APPROVED" if exc.status == "APPROVED" else "EXCEPTION_REJECTED",
        entity_type="EXCEPTION",
        entity_id=str(exc.id),
        metadata_json={"policy_id": str(exc.policy_id), "status": exc.status},
    )

    return exc


# ── Remediation CRUD ──────────────────────────────────────────────────────────


async def seed_default_remediations_if_empty(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Seed sample controlled remediation queue items if empty."""
    count_stmt = select(func.count()).select_from(FinOpsRemediationAction).where(
        FinOpsRemediationAction.user_id == user_id
    )
    res = await db.execute(count_stmt)
    if res.scalar_one() > 0:
        return

    now = datetime.now(UTC)
    sample_remediations = [
        (
            "stop_idle_compute",
            "dev-worker-n1-standard-8",
            "gcp",
            3800.00,
            "low",
            True,
            "DRY_RUN",
            "PENDING",
            "finops-automation@cloudpulse.ai",
        ),
        (
            "resize_resource",
            "prod-postgres-db-primary",
            "gcp",
            4900.00,
            "medium",
            True,
            "SIMULATED",
            "APPROVED",
            "sre-lead@cloudpulse.ai",
        ),
        (
            "delete_unattached_storage",
            "aws-s3-logs-and-backups",
            "aws",
            1250.00,
            "low",
            True,
            "DRY_RUN",
            "PENDING",
            "finops-analyst@cloudpulse.ai",
        ),
    ]

    for (
        a_type,
        res_name,
        prov,
        savings,
        risk,
        rb_supp,
        mode,
        app_status,
        req_by,
    ) in sample_remediations:
        rem = FinOpsRemediationAction(
            id=uuid.uuid4(),
            user_id=user_id,
            action_type=a_type,
            resource_name=res_name,
            provider=prov,
            estimated_savings=savings,
            risk_level=risk,
            rollback_supported=rb_supp,
            execution_mode=mode,
            approval_status=app_status,
            requested_by=req_by,
            original_config={"resource_name": res_name, "state": "running"},
            recommended_config={"resource_name": res_name, "state": "optimized"},
            rollback_config={"resource_name": res_name, "state": "running"},
            created_at=now,
            updated_at=now,
        )
        db.add(rem)

    await db.flush()


async def get_remediations(
    db: AsyncSession, *, user_id: uuid.UUID
) -> list[FinOpsRemediationAction]:
    """Fetch remediation actions."""
    await seed_default_remediations_if_empty(db, user_id)
    stmt = (
        select(FinOpsRemediationAction)
        .where(FinOpsRemediationAction.user_id == user_id)
        .order_by(FinOpsRemediationAction.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def request_remediation(
    db: AsyncSession, *, user_id: uuid.UUID, data: dict[str, Any], actor_email: str
) -> FinOpsRemediationAction:
    violation_id_val = None
    if data.get("violation_id"):
        try:
            v_uuid = uuid.UUID(str(data["violation_id"]))
            v_check = await db.execute(select(FinOpsCostViolation).where(FinOpsCostViolation.id == v_uuid))
            if v_check.scalar_one_or_none():
                violation_id_val = v_uuid
        except Exception:
            pass

    rem = FinOpsRemediationAction(
        id=uuid.uuid4(),
        user_id=user_id,
        violation_id=violation_id_val,
        action_type=data["action_type"],
        resource_name=data["resource_name"],
        provider=data["provider"],
        estimated_savings=float(data["estimated_savings"]),
        risk_level=data.get("risk_level", "low"),
        rollback_supported=True,
        execution_mode=data.get("execution_mode", "DRY_RUN"),
        approval_status="PENDING",
        requested_by=actor_email,
        original_config={"resource_name": data["resource_name"], "state": "running"},
        recommended_config={"resource_name": data["resource_name"], "state": "optimized"},
        rollback_config={"resource_name": data["resource_name"], "state": "running"},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(rem)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="REMEDIATION_REQUESTED",
        entity_type="REMEDIATION",
        entity_id=str(rem.id),
        metadata_json={"action_type": rem.action_type, "resource": rem.resource_name},
    )

    return rem


async def approve_remediation(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    remediation_id: uuid.UUID,
    status: str,
    actor_email: str,
) -> FinOpsRemediationAction | None:
    """Approve or reject a remediation request."""
    stmt = select(FinOpsRemediationAction).where(
        FinOpsRemediationAction.id == remediation_id,
        FinOpsRemediationAction.user_id == user_id,
    )
    res = await db.execute(stmt)
    rem = res.scalar_one_or_none()
    if not rem:
        return None

    rem.approval_status = status.upper()
    rem.approved_by = actor_email
    rem.updated_at = datetime.now(UTC)
    db.add(rem)
    await db.flush()

    await create_audit_log(
        db,
        user_id=user_id,
        actor_email=actor_email,
        action="REMEDIATION_APPROVED" if rem.approval_status == "APPROVED" else "REMEDIATION_REJECTED",
        entity_type="REMEDIATION",
        entity_id=str(rem.id),
        metadata_json={"action_type": rem.action_type, "status": rem.approval_status},
    )

    return rem
