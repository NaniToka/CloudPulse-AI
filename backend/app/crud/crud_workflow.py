"""
Repository for Workflows, Executions, Steps, Approvals, and Templates.
"""

import uuid
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.workflow import (
    Workflow,
    WorkflowApproval,
    WorkflowExecution,
    WorkflowStepLog,
    WorkflowTemplate,
)


class CRUDWorkflow(CRUDBase[Workflow, Any, Any]):
    async def get_multi_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: str | None = None,
        trigger_type: str | None = None,
        search: str | None = None,
    ) -> list[Workflow]:
        stmt = select(Workflow).where(Workflow.user_id == user_id)
        if status and status != "all":
            stmt = stmt.where(Workflow.status == status)
        if trigger_type and trigger_type != "all":
            stmt = stmt.where(Workflow.trigger_type == trigger_type)
        if search:
            stmt = stmt.where(Workflow.name.ilike(f"%{search}%"))
        res = await db.execute(stmt.order_by(Workflow.updated_at.desc()))
        return list(res.scalars().all())


class CRUDWorkflowExecution(CRUDBase[WorkflowExecution, Any, Any]):
    async def get_multi_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        workflow_id: uuid.UUID | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[WorkflowExecution]:
        stmt = (
            select(WorkflowExecution)
            .join(Workflow, Workflow.id == WorkflowExecution.workflow_id)
            .where(Workflow.user_id == user_id)
        )
        if workflow_id:
            stmt = stmt.where(WorkflowExecution.workflow_id == workflow_id)
        if status and status != "all":
            stmt = stmt.where(WorkflowExecution.status == status)
        res = await db.execute(stmt.order_by(WorkflowExecution.started_at.desc()).limit(limit))
        return list(res.scalars().all())


class CRUDWorkflowStepLog(CRUDBase[WorkflowStepLog, Any, Any]):
    async def get_by_execution(
        self, db: AsyncSession, execution_id: uuid.UUID
    ) -> list[WorkflowStepLog]:
        stmt = (
            select(WorkflowStepLog)
            .where(WorkflowStepLog.execution_id == execution_id)
            .order_by(WorkflowStepLog.created_at.asc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


class CRUDWorkflowApproval(CRUDBase[WorkflowApproval, Any, Any]):
    async def get_pending_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[WorkflowApproval]:
        stmt = (
            select(WorkflowApproval)
            .join(WorkflowExecution, WorkflowExecution.id == WorkflowApproval.execution_id)
            .join(Workflow, Workflow.id == WorkflowExecution.workflow_id)
            .where(and_(Workflow.user_id == user_id, WorkflowApproval.status == "pending"))
            .order_by(WorkflowApproval.requested_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


class CRUDWorkflowTemplate(CRUDBase[WorkflowTemplate, Any, Any]):
    async def get_all_templates(
        self, db: AsyncSession, category: str | None = None
    ) -> list[WorkflowTemplate]:
        stmt = select(WorkflowTemplate)
        if category and category != "all":
            stmt = stmt.where(WorkflowTemplate.category == category)
        res = await db.execute(stmt.order_by(WorkflowTemplate.name.asc()))
        return list(res.scalars().all())


crud_workflow = CRUDWorkflow(Workflow)
crud_workflow_execution = CRUDWorkflowExecution(WorkflowExecution)
crud_workflow_step_log = CRUDWorkflowStepLog(WorkflowStepLog)
crud_workflow_approval = CRUDWorkflowApproval(WorkflowApproval)
crud_workflow_template = CRUDWorkflowTemplate(WorkflowTemplate)
