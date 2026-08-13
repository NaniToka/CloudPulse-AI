"""
Central Execution Engine for Autonomous Operations.
Orchestrates validation, concurrency locking, policy checks, approval validation,
provider execution, post-verification, and audit logging.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous import (
    ExecutionLock,
    RemediationAuditLog,
    RemediationExecution,
    RemediationPlan,
)
from app.models.user import User
from app.services.autonomous import (
    approval_engine,
    precondition_engine,
    rollback_engine,
    verification_engine,
)
from app.services.autonomous.provider_adapters import get_provider_adapter

log = structlog.get_logger(__name__)


async def acquire_execution_lock(
    db: AsyncSession, resource_name: str, execution_id: uuid.UUID
) -> bool:
    """Acquires a concurrency lock for a target resource."""
    now = datetime.now(UTC)
    stmt = select(ExecutionLock).where(ExecutionLock.resource_name == resource_name)
    res = await db.execute(stmt)
    existing_lock = res.scalars().first()

    if existing_lock:
        if existing_lock.expires_at > now:
            return False  # Lock is active
        else:
            # Expired lock — cleanup
            await db.delete(existing_lock)
            await db.flush()

    new_lock = ExecutionLock(
        resource_name=resource_name,
        execution_id=execution_id,
        locked_at=now,
        expires_at=now + timedelta(minutes=5),
    )
    db.add(new_lock)
    try:
        await db.flush()
        return True
    except Exception:
        return False


async def release_execution_lock(db: AsyncSession, resource_name: str) -> None:
    """Releases a concurrency lock."""
    stmt = select(ExecutionLock).where(ExecutionLock.resource_name == resource_name)
    res = await db.execute(stmt)
    existing_lock = res.scalars().first()
    if existing_lock:
        await db.delete(existing_lock)
        await db.flush()


async def execute_remediation_plan(
    db: AsyncSession,
    *,
    plan: RemediationPlan,
    user: User | None = None,
    execution_mode: str | None = None,
) -> dict[str, Any]:
    """
    Executes a RemediationPlan through the complete autonomous pipeline.
    """
    mode = execution_mode or plan.execution_mode or "SIMULATED"
    idempotency_key = f"exec-{plan.id}-{uuid.uuid4().hex[:8]}"

    # 1. Create Execution Record in QUEUED state
    execution = RemediationExecution(
        plan_id=plan.id,
        user_id=user.id if user else plan.user_id,
        idempotency_key=idempotency_key,
        execution_mode=mode,
        status="QUEUED",
        rollback_status="ROLLBACK_AVAILABLE" if plan.rollback_supported else "NOT_SUPPORTED",
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # Audit Log: PLAN_EXECUTION_INITIATED
    audit_init = RemediationAuditLog(
        plan_id=plan.id,
        execution_id=execution.id,
        actor_id=user.id if user else None,
        action_type=plan.action_type,
        event_type="EXECUTION_INITIATED",
        target_resource=plan.affected_resource,
        provider=plan.provider,
        execution_mode=mode,
        details={"status": "QUEUED"},
    )
    db.add(audit_init)
    await db.commit()

    # 2. Acquire Concurrency Lock
    locked = await acquire_execution_lock(db, plan.affected_resource, execution.id)
    if not locked:
        execution.status = "BLOCKED"
        execution.error_message = f"Concurrency Lock: Resource '{plan.affected_resource}' is currently locked by another active operation."
        plan.status = "BLOCKED"
        await db.commit()
        return {
            "execution_id": str(execution.id),
            "status": "BLOCKED",
            "reason": execution.error_message,
        }

    try:
        # 3. Evaluate Preconditions
        execution.status = "VALIDATING"
        await db.commit()

        precond_res = await precondition_engine.evaluate_preconditions(
            db,
            action_type=plan.action_type,
            target_resource=plan.affected_resource,
            environment=plan.environment,
            provider=plan.provider,
            user=user,
        )
        execution.precondition_result = precond_res

        if not precond_res["passed"]:
            execution.status = "BLOCKED"
            execution.error_message = "; ".join(precond_res["reasons"])
            plan.status = "BLOCKED"
            await db.commit()
            return {
                "execution_id": str(execution.id),
                "status": "BLOCKED",
                "reasons": precond_res["reasons"],
            }

        # 4. Check Approval Requirements
        approval_res = await approval_engine.evaluate_approval_requirement(
            db,
            action_type=plan.action_type,
            environment=plan.environment,
            risk_level=plan.risk_level,
        )

        if approval_res["requires_approval"] and plan.status != "APPROVED":
            execution.status = "WAITING_APPROVAL"
            plan.status = "WAITING_APPROVAL"
            await db.commit()
            return {
                "execution_id": str(execution.id),
                "status": "WAITING_APPROVAL",
                "reason": approval_res["reason"],
            }

        # 5. Dispatch Action Execution via Provider Adapter
        execution.status = "EXECUTING"
        execution.started_at = datetime.now(UTC)
        await db.commit()

        adapter = get_provider_adapter(plan.provider, mode)

        act_type_upper = plan.action_type.upper()
        if "RESTART" in act_type_upper:
            exec_res = await adapter.restart_resource(plan.affected_resource)
        elif "SCALE" in act_type_upper:
            exec_res = await adapter.scale_resource(plan.affected_resource, replicas=6)
        elif "STOP" in act_type_upper:
            exec_res = await adapter.stop_resource(plan.affected_resource)
        elif "REMOVE" in act_type_upper or "DELETE" in act_type_upper:
            exec_res = await adapter.delete_resource(plan.affected_resource)
        else:
            exec_res = await adapter.restart_resource(plan.affected_resource)

        execution.execution_result = exec_res
        execution.previous_state = exec_res.get("previous_state", {})
        execution.new_state = exec_res.get("new_state", {})

        # 6. Post-Condition Verification
        execution.status = "VERIFYING"
        await db.commit()

        verify_res = await verification_engine.verify_postconditions(
            action_type=plan.action_type,
            target_resource=plan.affected_resource,
            provider=plan.provider,
            execution_mode=mode,
        )
        execution.verification_result = verify_res

        if verify_res["verified"]:
            execution.status = "COMPLETED"
            execution.completed_at = datetime.now(UTC)
            plan.status = "COMPLETED"
        else:
            execution.status = "FAILED"
            execution.error_message = "Post-condition verification failed: Target resource did not achieve expected healthy state."
            plan.status = "FAILED"

            # Auto Rollback if supported
            if plan.rollback_supported:
                await rollback_engine.execute_rollback(
                    db, execution=execution, provider=plan.provider, actor_id=user.id if user else None
                )

        # Audit Log Record
        audit_done = RemediationAuditLog(
            plan_id=plan.id,
            execution_id=execution.id,
            actor_id=user.id if user else None,
            action_type=plan.action_type,
            event_type="EXECUTION_COMPLETED" if execution.status == "COMPLETED" else "EXECUTION_FAILED",
            target_resource=plan.affected_resource,
            provider=plan.provider,
            execution_mode=mode,
            details={"status": execution.status, "verification": verify_res},
        )
        db.add(audit_done)
        await db.commit()
        await db.refresh(execution)

        return {
            "execution_id": str(execution.id),
            "status": execution.status,
            "execution_mode": mode,
            "result": exec_res,
            "verification_result": verify_res,
            "rollback_status": execution.rollback_status,
        }

    finally:
        await release_execution_lock(db, plan.affected_resource)
