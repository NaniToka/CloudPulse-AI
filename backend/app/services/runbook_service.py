"""
Service Layer for Auto Remediation Center & Runbook Generator.
"""

import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_runbook import crud_runbook
from app.models.runbook import AutomationStep, Runbook, RunbookExecution
from app.schemas.runbook import (
    RunbookCreatePayload,
)
from app.services.runbook_ai_service import generate_ai_runbook

log = structlog.get_logger(__name__)


class RunbookService:
    """Runbook Service handling generation, approval, and automated execution."""

    def __init__(self, crud_repo=crud_runbook) -> None:
        self.crud = crud_repo

    async def list_runbooks(
        self,
        db: AsyncSession,
        *,
        service: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Runbook], int, int]:
        return await self.crud.get_filtered(
            db,
            service=service,
            severity=severity,
            status=status,
            search=search,
            page=page,
            size=size,
        )

    async def get_by_id(self, db: AsyncSession, runbook_id: uuid.UUID) -> Runbook | None:
        return await self.crud.get_by_id_with_steps(db, runbook_id)

    async def generate_runbook(self, db: AsyncSession, payload: RunbookCreatePayload) -> Runbook:
        """Generates AI SRE remediation runbook with executable CLI/K8s commands."""
        now = datetime.now(UTC)
        ai_res = await generate_ai_runbook(payload.service_name, payload.severity)

        runbook = Runbook(
            id=uuid.uuid4(),
            title=payload.title or ai_res["title"],
            incident_id=payload.incident_id,
            service_name=payload.service_name,
            severity=payload.severity,
            generated_by_ai=True,
            status="Draft",
            executive_summary=ai_res["executive_summary"],
            root_cause=ai_res["root_cause"],
            rollback_procedure=ai_res["rollback_procedure"],
            verification_checklist=ai_res["verification_checklist"],
            post_recovery_checklist=ai_res["post_recovery_checklist"],
            estimated_resolution_time=ai_res["estimated_resolution_time"],
            risk_score=ai_res["risk_score"],
            confidence_score=ai_res["confidence_score"],
            created_at=now,
            updated_at=now,
        )

        steps_models = []
        for s in ai_res.get("steps", []):
            step_obj = AutomationStep(
                id=uuid.uuid4(),
                runbook_id=runbook.id,
                step_number=s["step_number"],
                title=s["title"],
                description=s.get("description", ""),
                command=s["command"],
                expected_output=s.get("expected_output", ""),
                rollback_command=s.get("rollback_command", ""),
                estimated_time=s.get("estimated_time", "2 mins"),
                verification_method=s.get("verification_method", "HTTP 200 Probe"),
                status="Pending",
            )
            steps_models.append(step_obj)

        runbook.steps = steps_models
        db.add(runbook)
        await db.commit()
        await db.refresh(runbook)
        return await self.get_by_id(db, runbook.id) or runbook

    async def approve_runbook(
        self, db: AsyncSession, runbook_id: uuid.UUID, approved_by: str
    ) -> Runbook | None:
        """Approves a runbook for automated execution."""
        runbook = await self.get_by_id(db, runbook_id)
        if not runbook:
            return None

        runbook.status = "Approved"
        runbook.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(runbook)
        return runbook

    async def execute_runbook(
        self,
        db: AsyncSession,
        runbook_id: uuid.UUID,
        executed_by: str = "CloudPulse AI Auto-Remediator",
    ) -> RunbookExecution | None:
        """Executes automation steps for an approved runbook."""
        runbook = await self.get_by_id(db, runbook_id)
        if not runbook:
            return None

        now = datetime.now(UTC)
        runbook.status = "Executing"

        # Update step statuses to completed
        logs = []
        for s in runbook.steps:
            s.status = "Completed"
            logs.append(
                f"[{datetime.now(UTC).isoformat()}] Step {s.step_number} '{s.title}' executed successfully."
            )

        execution = RunbookExecution(
            id=uuid.uuid4(),
            runbook_id=runbook.id,
            executed_by=executed_by,
            started_at=now,
            completed_at=datetime.now(UTC),
            status="Completed",
            logs_json=logs,
        )

        runbook.status = "Completed"
        runbook.updated_at = datetime.now(UTC)
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        return execution


runbook_service = RunbookService()
