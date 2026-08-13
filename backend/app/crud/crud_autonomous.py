"""
CRUD Operations for Autonomous Operations & Self-Healing Center.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous import (
    AutonomyPolicy,
    RemediationAuditLog,
    RemediationExecution,
    RemediationPlan,
)
from app.schemas.autonomous import (
    AutonomyPolicyUpdate,
    RemediationPlanCreate,
)


async def get_plans(
    db: AsyncSession, *, user_id: uuid.UUID | None = None, status: str | None = None, limit: int = 100
) -> list[RemediationPlan]:
    stmt = select(RemediationPlan).order_by(RemediationPlan.created_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(RemediationPlan.status == status.upper())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_plan_by_id(db: AsyncSession, plan_id: uuid.UUID) -> RemediationPlan | None:
    stmt = select(RemediationPlan).where(RemediationPlan.id == plan_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def create_plan(
    db: AsyncSession, *, plan_in: RemediationPlanCreate, user_id: uuid.UUID | None = None
) -> RemediationPlan:
    plan = RemediationPlan(
        user_id=user_id,
        trigger_source=plan_in.trigger_source,
        source_event_id=plan_in.source_event_id,
        root_cause=plan_in.root_cause,
        affected_resource=plan_in.affected_resource,
        provider=plan_in.provider,
        environment=plan_in.environment,
        action_type=plan_in.action_type.upper(),
        risk_level=plan_in.risk_level.upper(),
        expected_impact=plan_in.expected_impact,
        estimated_downtime_sec=plan_in.estimated_downtime_sec,
        estimated_cost_impact=plan_in.estimated_cost_impact,
        execution_mode=plan_in.execution_mode.upper(),
        status="PLANNED",
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def get_executions(
    db: AsyncSession, *, plan_id: uuid.UUID | None = None, limit: int = 100
) -> list[RemediationExecution]:
    stmt = select(RemediationExecution).order_by(RemediationExecution.created_at.desc()).limit(limit)
    if plan_id:
        stmt = stmt.where(RemediationExecution.plan_id == plan_id)
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_execution_by_id(db: AsyncSession, execution_id: uuid.UUID) -> RemediationExecution | None:
    stmt = select(RemediationExecution).where(RemediationExecution.id == execution_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_autonomy_policy(db: AsyncSession, user_id: uuid.UUID | None = None) -> AutonomyPolicy:
    stmt = select(AutonomyPolicy).where(AutonomyPolicy.is_active.is_(True))
    res = await db.execute(stmt)
    policy = res.scalars().first()

    if not policy:
        policy = AutonomyPolicy(
            user_id=user_id,
            autonomy_level=1,
            max_autonomous_risk="LOW",
            allowed_providers=["AWS", "Azure", "GCP", "Kubernetes"],
            allowed_environments=["development", "staging", "production"],
            default_execution_mode="SIMULATED",
            is_active=True,
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)

    return policy


async def update_autonomy_policy(
    db: AsyncSession, *, policy_in: AutonomyPolicyUpdate, user_id: uuid.UUID | None = None
) -> AutonomyPolicy:
    policy = await get_autonomy_policy(db, user_id=user_id)
    policy.autonomy_level = policy_in.autonomy_level
    policy.max_autonomous_risk = policy_in.max_autonomous_risk.upper()
    policy.allowed_providers = policy_in.allowed_providers
    policy.allowed_environments = policy_in.allowed_environments
    policy.excluded_resources = policy_in.excluded_resources
    policy.excluded_namespaces = policy_in.excluded_namespaces
    policy.default_execution_mode = policy_in.default_execution_mode.upper()
    policy.is_active = policy_in.is_active

    await db.commit()
    await db.refresh(policy)
    return policy


async def get_audit_logs(db: AsyncSession, limit: int = 100) -> list[RemediationAuditLog]:
    stmt = select(RemediationAuditLog).order_by(RemediationAuditLog.created_at.desc()).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())
