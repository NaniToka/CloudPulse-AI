"""
Autonomous AIOps Agent REST API Endpoints.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.aiops import (
    AgentAnalyzePayload,
    AgentApprovePayload,
    AgentRecommendationResponse,
    AIOpsAgentStatusResponse,
    AIOpsListResponse,
)
from app.services.aiops_service import AIOpsService, aiops_service

log = structlog.get_logger(__name__)

router = APIRouter()


def get_aiops_service() -> AIOpsService:
    return aiops_service


async def _seed_initial_aiops_recommendations(db: AsyncSession, service: AIOpsService) -> None:
    items, total, _ = await service.list_recommendations(db, size=1)
    if total == 0:
        log.info("seeding_initial_aiops_recommendations")
        await service.trigger_agent_loop(db, AgentAnalyzePayload(target_system="Metrics"))
        await service.trigger_agent_loop(db, AgentAnalyzePayload(target_system="Traces"))
        await service.trigger_agent_loop(db, AgentAnalyzePayload(target_system="Security"))


@router.get(
    "/status",
    response_model=AIOpsAgentStatusResponse,
    summary="Get live Autonomous AIOps Agent status",
)
async def get_agent_status(
    db: AsyncSession = Depends(get_db),
    service: AIOpsService = Depends(get_aiops_service),
):
    """Retrieve live AIOps agent loop phase, health status, and active tasks."""
    agent = await service.get_agent_status(db)
    recs, total, _ = await service.list_recommendations(db, size=100)
    pending = len([r for r in recs if r.status == "Pending_Approval"])

    resp = AIOpsAgentStatusResponse.model_validate(agent)
    resp.total_recommendations = total
    resp.pending_approvals = pending
    resp.active_automations = len([r for r in recs if r.status == "Executed"])
    return resp


@router.get("/recommendations", response_model=AIOpsListResponse, summary="List AI recommendations")
async def list_recommendations(
    category: str | None = Query(
        None,
        description="Filter by category (Root_Cause, Anomaly_Detection, Performance, Cost_Optimization)",
    ),
    priority: str | None = Query(None, description="Filter by priority (P0, P1, P2, P3)"),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by status (Pending_Approval, Approved, Executed)"
    ),
    search: str | None = Query(None, description="Search in title or root cause"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: AIOpsService = Depends(get_aiops_service),
):
    """Retrieve paginated AIOps recommendations."""
    await _seed_initial_aiops_recommendations(db, service)
    items, total, pages = await service.list_recommendations(
        db,
        category=category,
        priority=priority,
        status=status_filter,
        search=search,
        page=page,
        size=size,
    )
    return AIOpsListResponse(
        items=[AgentRecommendationResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "/analyze",
    response_model=AgentRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger autonomous agent loop",
)
async def trigger_autonomous_analysis(
    payload: AgentAnalyzePayload,
    db: AsyncSession = Depends(get_db),
    service: AIOpsService = Depends(get_aiops_service),
):
    """Trigger the 6-phase Agent Loop (Observe -> Detect -> Analyze -> Plan -> Recommend -> Verify)."""
    rec = await service.trigger_agent_loop(db, payload)
    return AgentRecommendationResponse.model_validate(rec)


@router.post(
    "/approve",
    response_model=AgentRecommendationResponse,
    summary="Approve or Reject recommendation",
)
async def approve_recommendation(
    payload: AgentApprovePayload,
    db: AsyncSession = Depends(get_db),
    service: AIOpsService = Depends(get_aiops_service),
):
    """Approve or Reject an AIOps recommendation for automated execution."""
    updated = await service.approve_or_reject_recommendation(db, payload)
    if not updated:
        raise HTTPException(
            status_code=404, detail=f"Recommendation '{payload.recommendation_id}' not found."
        )
    return AgentRecommendationResponse.model_validate(updated)


@router.get("/history", summary="Get execution audit history")
async def get_execution_history(
    db: AsyncSession = Depends(get_db),
    service: AIOpsService = Depends(get_aiops_service),
):
    """Retrieve audit history log of approved and executed AIOps recommendations."""
    recs, total, _ = await service.list_recommendations(db, status="Executed", size=50)
    return {
        "total_executions": total,
        "history": [AgentRecommendationResponse.model_validate(r) for r in recs],
    }
