"""
Auto Remediation Center REST API Endpoints.
"""

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.runbook import (
    RunbookApprovePayload,
    RunbookCreatePayload,
    RunbookExecutionResponse,
    RunbookListResponse,
    RunbookResponse,
)
from app.services.runbook_service import RunbookService, runbook_service

log = structlog.get_logger(__name__)

router = APIRouter()


def get_runbook_service() -> RunbookService:
    return runbook_service


async def _seed_initial_runbooks_if_empty(db: AsyncSession, service: RunbookService) -> None:
    rb_list, total, _ = await service.list_runbooks(db, size=1)
    if total == 0:
        log.info("seeding_initial_remediation_runbooks")
        sample_payloads = [
            RunbookCreatePayload(
                incident_id="INC-4029",
                service_name="api-gateway",
                severity="P0",
                title="Automated SRE Remediation Runbook: OOM & Memory Heap Recovery",
            ),
            RunbookCreatePayload(
                incident_id="INC-3882",
                service_name="auth-service",
                severity="P1",
                title="Database Connection Pool Exhaustion Mitigation",
            ),
            RunbookCreatePayload(
                incident_id=None,
                service_name="billing-service",
                severity="P2",
                title="External Payment Gateway Retry & Circuit Breaker Tuning",
            ),
        ]
        for payload in sample_payloads:
            await service.generate_runbook(db, payload)


@router.post(
    "/generate",
    response_model=RunbookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI remediation runbook",
)
async def generate_runbook(
    payload: RunbookCreatePayload,
    db: AsyncSession = Depends(get_db),
    service: RunbookService = Depends(get_runbook_service),
):
    """Generate step-by-step SRE remediation runbook with executable CLI/K8s/Terraform commands using Gemini AI."""
    runbook = await service.generate_runbook(db, payload)
    return RunbookResponse.model_validate(runbook)


@router.get("", response_model=RunbookListResponse, summary="List remediation runbooks")
async def list_runbooks(
    service_name: str | None = Query(None, description="Filter by service name"),
    severity: str | None = Query(None, description="Filter by severity (P0, P1, P2, P3)"),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by status (Draft, Approved, Completed)"
    ),
    search: str | None = Query(None, description="Search in title or root cause"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: RunbookService = Depends(get_runbook_service),
):
    """Retrieve paginated list of remediation runbooks."""
    await _seed_initial_runbooks_if_empty(db, service)
    items, total, pages = await service.list_runbooks(
        db,
        service=service_name,
        severity=severity,
        status=status_filter,
        search=search,
        page=page,
        size=size,
    )
    return RunbookListResponse(
        items=[RunbookResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{runbook_id}",
    response_model=RunbookResponse,
    summary="Get runbook details & automation steps",
)
async def get_runbook(
    runbook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: RunbookService = Depends(get_runbook_service),
):
    """Retrieve single runbook with complete automation step commands."""
    await _seed_initial_runbooks_if_empty(db, service)
    runbook = await service.get_by_id(db, runbook_id)
    if not runbook:
        raise HTTPException(status_code=404, detail=f"Runbook '{runbook_id}' not found.")
    return RunbookResponse.model_validate(runbook)


@router.post(
    "/{runbook_id}/approve", response_model=RunbookResponse, summary="Approve runbook for execution"
)
async def approve_runbook(
    runbook_id: uuid.UUID,
    payload: RunbookApprovePayload,
    db: AsyncSession = Depends(get_db),
    service: RunbookService = Depends(get_runbook_service),
):
    """Approve a draft runbook for automated execution."""
    updated = await service.approve_runbook(db, runbook_id, payload.approved_by)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Runbook '{runbook_id}' not found.")
    return RunbookResponse.model_validate(updated)


@router.post(
    "/{runbook_id}/execute",
    response_model=RunbookExecutionResponse,
    summary="Execute runbook automation steps",
)
async def execute_runbook(
    runbook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: RunbookService = Depends(get_runbook_service),
):
    """Trigger automated execution of runbook CLI/K8s commands."""
    execution = await service.execute_runbook(db, runbook_id)
    if not execution:
        raise HTTPException(
            status_code=404, detail=f"Runbook '{runbook_id}' not found or not approved."
        )
    return RunbookExecutionResponse.model_validate(execution)
