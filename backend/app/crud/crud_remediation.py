"""
CRUD Repository for Enterprise AIOps Automated Remediation & Action Center.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous import (
    RemediationAuditLog,
    RemediationExecution,
    RemediationPlan,
    RemediationPolicyRecord,
)
from app.schemas.remediation import RemediationPolicyCreate, RemediationPolicyUpdate


class CRUDRemediation:
    """CRUD repository managing remediation entities and audit trails."""

    async def get_plan(self, db: AsyncSession, plan_id: uuid.UUID) -> RemediationPlan | None:
        stmt = select(RemediationPlan).where(RemediationPlan.id == plan_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    async def get_plans(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None = None,
        status: str | None = None,
        provider: str | None = None,
        risk_level: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RemediationPlan]:
        stmt = select(RemediationPlan)
        if user_id:
            stmt = stmt.where(RemediationPlan.user_id == user_id)
        if status:
            stmt = stmt.where(RemediationPlan.status == status.upper())
        if provider:
            stmt = stmt.where(RemediationPlan.provider == provider)
        if risk_level:
            stmt = stmt.where(RemediationPlan.risk_level == risk_level.upper())
        stmt = stmt.order_by(RemediationPlan.created_at.desc()).limit(limit).offset(offset)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def create_plan(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None,
        trigger_source: str,
        source_event_id: str | None,
        root_cause: str,
        affected_resource: str,
        provider: str,
        environment: str,
        action_type: str,
        risk_level: str,
        expected_impact: str,
        estimated_downtime_sec: int,
        estimated_cost_impact: float,
        requires_approval: bool,
        rollback_supported: bool,
        execution_mode: str,
        confidence_score: float = 0.92,
        status: str = "PLANNED",
        plan_details: dict[str, Any] | None = None,
    ) -> RemediationPlan:
        plan = RemediationPlan(
            user_id=user_id,
            trigger_source=trigger_source,
            source_event_id=source_event_id,
            root_cause=root_cause,
            affected_resource=affected_resource,
            provider=provider,
            environment=environment,
            action_type=action_type,
            risk_level=risk_level,
            expected_impact=expected_impact,
            estimated_downtime_sec=estimated_downtime_sec,
            estimated_cost_impact=estimated_cost_impact,
            requires_approval=requires_approval,
            rollback_supported=rollback_supported,
            execution_mode=execution_mode,
            confidence_score=confidence_score,
            status=status,
            plan_details=plan_details or {},
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan

    async def get_execution(self, db: AsyncSession, execution_id: uuid.UUID) -> RemediationExecution | None:
        stmt = select(RemediationExecution).where(RemediationExecution.id == execution_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    async def get_execution_by_idempotency_key(
        self, db: AsyncSession, idempotency_key: str
    ) -> RemediationExecution | None:
        stmt = select(RemediationExecution).where(RemediationExecution.idempotency_key == idempotency_key)
        res = await db.execute(stmt)
        return res.scalars().first()

    async def get_executions(
        self,
        db: AsyncSession,
        *,
        plan_id: uuid.UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RemediationExecution]:
        stmt = select(RemediationExecution)
        if plan_id:
            stmt = stmt.where(RemediationExecution.plan_id == plan_id)
        if status:
            stmt = stmt.where(RemediationExecution.status == status.upper())
        stmt = stmt.order_by(RemediationExecution.created_at.desc()).limit(limit).offset(offset)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def create_policy(
        self, db: AsyncSession, policy_in: RemediationPolicyCreate, created_by: str = "system"
    ) -> RemediationPolicyRecord:
        policy = RemediationPolicyRecord(
            name=policy_in.name,
            trigger_signal=policy_in.trigger_signal,
            condition_logic=policy_in.condition_logic,
            action_type=policy_in.action_type,
            risk_level=policy_in.risk_level,
            execution_mode=policy_in.execution_mode,
            cooldown_minutes=policy_in.cooldown_minutes,
            is_enabled=policy_in.is_enabled,
            created_by=created_by,
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    async def get_policy(self, db: AsyncSession, policy_id: uuid.UUID) -> RemediationPolicyRecord | None:
        stmt = select(RemediationPolicyRecord).where(RemediationPolicyRecord.id == policy_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    async def get_policies(
        self, db: AsyncSession, *, is_enabled: bool | None = None, limit: int = 100
    ) -> list[RemediationPolicyRecord]:
        stmt = select(RemediationPolicyRecord)
        if is_enabled is not None:
            stmt = stmt.where(RemediationPolicyRecord.is_enabled == is_enabled)
        stmt = stmt.order_by(RemediationPolicyRecord.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def update_policy(
        self, db: AsyncSession, policy: RemediationPolicyRecord, policy_in: RemediationPolicyUpdate
    ) -> RemediationPolicyRecord:
        update_data = policy_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    async def get_audit_logs(
        self, db: AsyncSession, *, plan_id: uuid.UUID | None = None, limit: int = 100
    ) -> list[RemediationAuditLog]:
        stmt = select(RemediationAuditLog)
        if plan_id:
            stmt = stmt.where(RemediationAuditLog.plan_id == plan_id)
        stmt = stmt.order_by(RemediationAuditLog.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())


crud_remediation = CRUDRemediation()
