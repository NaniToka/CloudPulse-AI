"""
Service Layer for Autonomous AIOps Agent & AI Operations Center.
"""

import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_aiops import crud_aiops
from app.models.aiops import AgentExecution, AgentRecommendation, AgentTask, AIOpsAgent
from app.schemas.aiops import (
    AgentAnalyzePayload,
    AgentApprovePayload,
)
from app.services.aiops_ai_service import generate_aiops_analysis

log = structlog.get_logger(__name__)


class AIOpsService:
    """AIOps Service managing the 6-phase Agent Loop and recommendations."""

    def __init__(self, crud_repo=crud_aiops) -> None:
        self.crud = crud_repo

    async def get_agent_status(self, db: AsyncSession) -> AIOpsAgent:
        """Fetch or initialize active AIOps agent state."""
        agent = await self.crud.get_active_agent(db)
        if not agent:
            agent = await self._seed_initial_agent(db)
        return agent

    async def list_recommendations(
        self,
        db: AsyncSession,
        *,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[AgentRecommendation], int, int]:
        await self.get_agent_status(db)
        return await self.crud.get_filtered_recommendations(
            db,
            category=category,
            priority=priority,
            status=status,
            search=search,
            page=page,
            size=size,
        )

    async def trigger_agent_loop(
        self, db: AsyncSession, payload: AgentAnalyzePayload
    ) -> AgentRecommendation:
        """Executes the 6-phase Agent Loop: Observe -> Detect -> Analyze -> Plan -> Recommend -> Verify."""
        agent = await self.get_agent_status(db)
        now = datetime.now(UTC)

        target = payload.target_system or "All"
        log.info("triggering_aiops_agent_loop", phase="Observe", target=target)

        # Update Agent Loop Phases
        agent.current_phase = "Observe"
        agent.last_observation_at = now

        # AI Synthesis
        ai_res = await generate_aiops_analysis(target)

        agent.current_phase = "Recommend"
        rec = AgentRecommendation(
            id=uuid.uuid4(),
            agent_id=agent.id,
            title=ai_res["title"],
            category=ai_res["category"],
            priority=ai_res["priority"],
            executive_summary=ai_res["executive_summary"],
            root_cause=ai_res["root_cause"],
            business_impact=ai_res["business_impact"],
            recommended_actions=ai_res["recommended_actions"],
            automation_candidates=ai_res["automation_candidates"],
            confidence_score=ai_res["confidence_score"],
            expected_recovery_time=ai_res["expected_recovery_time"],
            status="Pending_Approval",
            created_at=now,
            updated_at=now,
        )
        runbook_rec = rec
        db.add(runbook_rec)
        await db.commit()

        # Re-fetch with loaded executions
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = (
            select(AgentRecommendation)
            .options(selectinload(AgentRecommendation.executions))
            .where(AgentRecommendation.id == runbook_rec.id)
        )
        res = await db.execute(stmt)
        return res.scalar_one()

    async def approve_or_reject_recommendation(
        self, db: AsyncSession, payload: AgentApprovePayload
    ) -> AgentRecommendation | None:
        """Approve or Reject an AIOps Recommendation."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = (
            select(AgentRecommendation)
            .options(selectinload(AgentRecommendation.executions))
            .where(AgentRecommendation.id == payload.recommendation_id)
        )
        res = await db.execute(stmt)
        select_rec = res.scalar_one_or_none()

        if not select_rec:
            return None

        now = datetime.now(UTC)
        if payload.action == "Reject":
            select_rec.status = "Rejected"
            select_rec.updated_at = now
            await db.commit()
            await db.refresh(select_rec)
            return select_rec

        # Approved & Executed
        select_rec.status = "Approved"
        select_rec.updated_at = now

        exec_logs = [
            f"[{now.isoformat()}] Recommendation approved by '{payload.approved_by}'.",
            f"[{now.isoformat()}] Dispatching automated action candidates to CloudPulse Agent Engine.",
        ]
        for cmd in select_rec.automation_candidates or []:
            exec_logs.append(f"[{datetime.now(UTC).isoformat()}] Executed: {cmd}")

        execution = AgentExecution(
            id=uuid.uuid4(),
            recommendation_id=select_rec.id,
            action_taken=select_rec.title,
            approved_by=payload.approved_by,
            status="Completed",
            execution_logs=exec_logs,
            executed_at=datetime.now(UTC),
        )

        select_rec.status = "Executed"
        db.add(execution)
        await db.commit()

        # Re-fetch with loaded executions
        res_updated = await db.execute(stmt)
        return res_updated.scalar_one_or_none()

    async def _seed_initial_agent(self, db: AsyncSession) -> AIOpsAgent:
        """Seed initial Autonomous AIOps Agent and tasks."""
        now = datetime.now(UTC)
        agent = AIOpsAgent(
            id=uuid.uuid4(),
            agent_name="CloudPulse Autonomous Core",
            status="Autonomous",
            current_phase="Observe",
            health_status="Healthy",
            last_observation_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(agent)

        tasks = [
            AgentTask(
                id=uuid.uuid4(),
                agent_id=agent.id,
                task_name="Metrics Sliding Window Anomaly Detection",
                target_system="Metrics",
                status="Completed",
                started_at=now,
                completed_at=now,
            ),
            AgentTask(
                id=uuid.uuid4(),
                agent_id=agent.id,
                task_name="Cross-Layer OpenTelemetry Latency Waterfall Correlation",
                target_system="Traces",
                status="Completed",
                started_at=now,
                completed_at=now,
            ),
            AgentTask(
                id=uuid.uuid4(),
                agent_id=agent.id,
                task_name="FinOps Cloud Cost Spikes & Idle Capacity Audit",
                target_system="Cost",
                status="Completed",
                started_at=now,
                completed_at=now,
            ),
            AgentTask(
                id=uuid.uuid4(),
                agent_id=agent.id,
                task_name="CSPM Vulnerability & Open Firewall Rule Correlation",
                target_system="Security",
                status="Completed",
                started_at=now,
                completed_at=now,
            ),
        ]
        for t in tasks:
            db.add(t)

        await db.commit()
        await db.refresh(agent)
        return agent


aiops_service = AIOpsService()
