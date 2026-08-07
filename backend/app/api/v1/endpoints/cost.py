"""
Cloud Cost Optimizer API endpoints.

Routes
------
GET    /api/v1/cost/overview          — Monthly cost, trend, service & region breakdown
GET    /api/v1/cost/services          — Detailed service-wise spending breakdown
GET    /api/v1/cost/recommendations    — AI optimization recommendations
POST   /api/v1/cost/analyze          — Trigger Gemini AI FinOps cost analysis
GET    /api/v1/cost/resources        — Resource inventory list with cost & status
PATCH  /api/v1/cost/recommendations/{id}/status — Update recommendation status
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_cost
from app.models.user import User
from app.schemas.cost import (
    CloudCostItem,
    CloudCostListResponse,
    CostAnalyzeResponse,
    CostOverviewResponse,
    DailyCostItem,
    RecommendationItem,
    RecommendationsResponse,
    RegionCostItem,
    ServiceCostItem,
    ServiceCostsResponse,
)
from app.services.cost_ai_service import analyze_cloud_costs_with_gemini

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /cost/overview
# ---------------------------------------------------------------------------


@router.get(
    "/overview",
    response_model=CostOverviewResponse,
    summary="Get cost overview metrics, trends, and service/region breakdowns",
)
async def get_cost_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostOverviewResponse:
    log.info("get_cost_overview", user_id=str(current_user.id))
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)

    return CostOverviewResponse(
        monthly_cost=data["monthly_cost"],
        previous_month_cost=data["previous_month_cost"],
        percentage_change=data["percentage_change"],
        projected_cost=data["projected_cost"],
        potential_savings=data["potential_savings"],
        efficiency_score=data["efficiency_score"],
        active_resources_count=data["active_resources_count"],
        idle_resources_count=data["idle_resources_count"],
        daily_trend=[DailyCostItem(**d) for d in data["daily_trend"]],
        service_breakdown=[ServiceCostItem(**s) for s in data["service_breakdown"]],
        region_breakdown=[RegionCostItem(**r) for r in data["region_breakdown"]],
    )


# ---------------------------------------------------------------------------
# GET /cost/services
# ---------------------------------------------------------------------------


@router.get(
    "/services",
    response_model=ServiceCostsResponse,
    summary="Get detailed service-wise spending breakdown",
)
async def get_service_costs(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceCostsResponse:
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)
    services = [ServiceCostItem(**s) for s in data["service_breakdown"]]
    total = sum(s.cost for s in services)

    return ServiceCostsResponse(
        services=services,
        total_cost=round(total, 2),
    )


# ---------------------------------------------------------------------------
# GET /cost/recommendations
# ---------------------------------------------------------------------------


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="List AI optimization recommendations",
)
async def get_recommendations(
    status_filter: str | None = Query(default="active", alias="status"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationsResponse:
    items, total_savings = await crud_cost.get_recommendations(
        db, user_id=current_user.id, status=status_filter
    )
    return RecommendationsResponse(
        items=[RecommendationItem.model_validate(r) for r in items],
        total=len(items),
        total_savings=total_savings,
    )


# ---------------------------------------------------------------------------
# POST /cost/analyze
# ---------------------------------------------------------------------------


@router.post(
    "/analyze",
    response_model=CostAnalyzeResponse,
    summary="Trigger Gemini AI Cloud FinOps cost analysis",
)
async def analyze_costs(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostAnalyzeResponse:
    log.info("trigger_cost_analysis", user_id=str(current_user.id))

    overview = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, limit=50)

    resources_dicts = [
        {
            "resource_name": c.resource_name,
            "service": c.service,
            "cost": c.cost,
            "region": c.region,
            "status": c.status,
            "environment": c.environment,
        }
        for c in costs
    ]

    try:
        analysis = await analyze_cloud_costs_with_gemini(
            db,
            user_id=str(current_user.id),
            costs_overview=overview,
            resources=resources_dicts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    except Exception as exc:
        log.exception("cost_analysis_endpoint_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI cost analysis failed: {str(exc)}",
        )

    # Convert recommendation objects if present
    recs_out = []
    for r in analysis.get("recommendations", []):
        if isinstance(r, RecommendationItem):
            recs_out.append(r)
        elif hasattr(r, "id"):
            recs_out.append(RecommendationItem.model_validate(r))

    return CostAnalyzeResponse(
        cost_summary=analysis.get("cost_summary", ""),
        highest_cost_services=analysis.get("highest_cost_services", []),
        idle_resources=analysis.get("idle_resources", []),
        wasted_resources=analysis.get("wasted_resources", []),
        optimization_suggestions=analysis.get("optimization_suggestions", []),
        reserved_instance_recommendations=analysis.get("reserved_instance_recommendations", []),
        auto_scaling_recommendations=analysis.get("auto_scaling_recommendations", []),
        estimated_monthly_savings=float(analysis.get("estimated_monthly_savings", 0.0)),
        recommendations=recs_out,
        efficiency_score=int(analysis.get("efficiency_score", 75)),
        analyzed_at=analysis.get("analyzed_at"),
    )


# ---------------------------------------------------------------------------
# GET /cost/resources
# ---------------------------------------------------------------------------


@router.get(
    "/resources",
    response_model=CloudCostListResponse,
    summary="List resource cost inventory with filters and search",
)
async def get_resource_costs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: str | None = None,
    region: str | None = None,
    search: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CloudCostListResponse:
    items, total = await crud_cost.get_costs(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        service=service,
        region=region,
        search=search,
    )
    return CloudCostListResponse(
        items=[CloudCostItem.model_validate(c) for c in items],
        total=total,
    )


# ---------------------------------------------------------------------------
# PATCH /cost/recommendations/{id}/status
# ---------------------------------------------------------------------------


@router.patch(
    "/recommendations/{recommendation_id}/status",
    response_model=RecommendationItem,
    summary="Update recommendation status (active | dismissed | applied)",
)
async def update_recommendation_status(
    recommendation_id: uuid.UUID,
    status_value: str = Query(..., alias="status"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationItem:
    if status_value not in ("active", "dismissed", "applied"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be one of: active, dismissed, applied",
        )

    updated = await crud_cost.update_recommendation_status(
        db,
        user_id=current_user.id,
        recommendation_id=recommendation_id,
        status=status_value,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization recommendation not found",
        )
    return RecommendationItem.model_validate(updated)
