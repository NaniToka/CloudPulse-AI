"""
Enterprise FinOps & Cloud Cost Optimizer API endpoints.

Routes:
-------
GET    /api/v1/cost/overview        — Overall spending metrics, provider & region breakdowns
GET    /api/v1/cost/trends          — Daily & monthly spending trends with projections
GET    /api/v1/cost/providers       — Provider-level cost breakdown (AWS, Azure, GCP, K8s)
GET    /api/v1/cost/services        — Service-level cost breakdown
GET    /api/v1/cost/regions         — Regional spending breakdown
GET    /api/v1/cost/resources       — Detailed resource inventory with cost & status
GET    /api/v1/cost/anomalies       — Calculated cost anomalies & spending spikes
GET    /api/v1/cost/forecast        — 7-day, 30-day, and month-end trend forecasts
GET    /api/v1/cost/budgets         — List FinOps budgets with threshold evaluation
POST   /api/v1/cost/budgets         — Create new cost budget
PUT    /api/v1/cost/budgets/{id}    — Update existing budget parameters
GET    /api/v1/cost/optimization    — List optimization recommendations
GET    /api/v1/cost/savings         — Total monthly & annual savings opportunities
POST   /api/v1/cost/analyze         — Trigger Gemini AI / Local FinOps cost analysis
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
    CostAnomaliesResponse,
    CostAnomalyItem,
    CostBudgetItem,
    CostBudgetListResponse,
    CostBudgetPayload,
    CostForecastResponse,
    CostOverviewResponse,
    CostSavingsResponse,
    CostTrendsResponse,
    DailyCostItem,
    ProviderCostItem,
    ProviderCostsResponse,
    RecommendationItem,
    RecommendationsResponse,
    RegionCostItem,
    RegionCostsResponse,
    ServiceCostItem,
    ServiceCostsResponse,
)
from app.services.cost_ai_service import analyze_cloud_costs_with_gemini
from app.services.cost_engine import (
    calculate_cost_forecast,
    calculate_savings_summary,
    detect_cost_anomalies,
    evaluate_budget,
    group_costs_by_provider,
    group_costs_by_region,
    group_costs_by_service,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /cost/overview
# ---------------------------------------------------------------------------


@router.get(
    "/overview",
    response_model=CostOverviewResponse,
    summary="Get comprehensive cost overview metrics, trends, and multi-cloud breakdowns",
)
async def get_cost_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostOverviewResponse:
    log.info("get_cost_overview", user_id=str(current_user.id))
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, limit=200)

    resources_dicts = [
        {"cost": c.cost, "provider": c.provider, "service": c.service, "region": c.region}
        for c in costs
    ]
    provider_breakdown = group_costs_by_provider(resources_dicts)

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
        provider_breakdown=[ProviderCostItem(**p) for p in provider_breakdown],
        data_source="Demo Data — No Cloud Credentials Connected",
        environment="Local Development",
    )


# ---------------------------------------------------------------------------
# GET /cost/trends
# ---------------------------------------------------------------------------


@router.get(
    "/trends",
    response_model=CostTrendsResponse,
    summary="Get daily & monthly spending trends with projections",
)
async def get_cost_trends(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostTrendsResponse:
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)
    daily_items = [DailyCostItem(**d) for d in data["daily_trend"]]
    forecast = calculate_cost_forecast(data["daily_trend"], data["monthly_cost"])

    return CostTrendsResponse(
        daily_trend=daily_items,
        monthly_trend=[
            DailyCostItem(date="Previous Month", cost=data["previous_month_cost"]),
            DailyCostItem(date="Current Month", cost=data["monthly_cost"]),
            DailyCostItem(date="Projected Month-End", cost=data["projected_cost"]),
        ],
        projected_cost=data["projected_cost"],
        trend_direction=forecast["trend_direction"],
    )


# ---------------------------------------------------------------------------
# GET /cost/providers
# ---------------------------------------------------------------------------


@router.get(
    "/providers",
    response_model=ProviderCostsResponse,
    summary="Get cloud provider spending breakdown (AWS, Azure, GCP, K8s)",
)
async def get_provider_costs(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProviderCostsResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, limit=300)
    resources_dicts = [
        {"cost": c.cost, "provider": c.provider, "service": c.service} for c in costs
    ]
    providers = [ProviderCostItem(**p) for p in group_costs_by_provider(resources_dicts)]
    total = sum(p.cost for p in providers)

    return ProviderCostsResponse(
        providers=providers,
        total_cost=round(total, 2),
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
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, limit=300)
    resources_dicts = [{"cost": c.cost, "service": c.service} for c in costs]
    services = [ServiceCostItem(**s) for s in group_costs_by_service(resources_dicts)]
    total = sum(s.cost for s in services)

    return ServiceCostsResponse(
        services=services,
        total_cost=round(total, 2),
    )


# ---------------------------------------------------------------------------
# GET /cost/regions
# ---------------------------------------------------------------------------


@router.get(
    "/regions",
    response_model=RegionCostsResponse,
    summary="Get regional spending breakdown",
)
async def get_region_costs(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RegionCostsResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, limit=300)
    resources_dicts = [{"cost": c.cost, "region": c.region} for c in costs]
    regions = [RegionCostItem(**r) for r in group_costs_by_region(resources_dicts)]
    total = sum(r.cost for r in regions)

    return RegionCostsResponse(
        regions=regions,
        total_cost=round(total, 2),
    )


# ---------------------------------------------------------------------------
# GET /cost/anomalies
# ---------------------------------------------------------------------------


@router.get(
    "/anomalies",
    response_model=CostAnomaliesResponse,
    summary="Detect spending anomalies and spikes",
)
async def get_cost_anomalies(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostAnomaliesResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, limit=300)
    resources_dicts = [
        {
            "cost": c.cost,
            "status": c.status,
            "resource_name": c.resource_name,
            "service": c.service,
            "provider": c.provider,
        }
        for c in costs
    ]
    raw_anomalies = detect_cost_anomalies(resources_dicts)
    anomaly_items = [CostAnomalyItem(**a) for a in raw_anomalies]
    crit_count = sum(1 for a in anomaly_items if a.severity == "CRITICAL")

    return CostAnomaliesResponse(
        anomalies=anomaly_items,
        total_anomalies=len(anomaly_items),
        critical_anomalies=crit_count,
    )


# ---------------------------------------------------------------------------
# GET /cost/forecast
# ---------------------------------------------------------------------------


@router.get(
    "/forecast",
    response_model=CostForecastResponse,
    summary="Get 7-day, 30-day, and month-end forecasts with confidence metrics",
)
async def get_cost_forecast(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostForecastResponse:
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id)
    fc = calculate_cost_forecast(data["daily_trend"], data["monthly_cost"])
    return CostForecastResponse(**fc)


# ---------------------------------------------------------------------------
# GET /cost/budgets
# ---------------------------------------------------------------------------


@router.get(
    "/budgets",
    response_model=CostBudgetListResponse,
    summary="List FinOps budgets with threshold evaluation",
)
async def get_cost_budgets(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostBudgetListResponse:
    budgets_db = await crud_cost.get_budgets(db, user_id=current_user.id)

    out_budgets = []
    for b in budgets_db:
        current_spend = await crud_cost.calculate_budget_spend(
            db,
            user_id=current_user.id,
            provider=b.provider,
            service=b.service,
            environment=b.environment,
        )
        projected_spend = round(current_spend * 1.05, 2)
        ev = evaluate_budget(b.amount, current_spend, projected_spend)
        out_budgets.append(
            CostBudgetItem(
                id=b.id,
                name=b.name,
                provider=b.provider,
                service=b.service,
                environment=b.environment,
                amount=b.amount,
                current_spend=ev["current_spend"],
                utilization_pct=ev["utilization_pct"],
                projected_spend=ev["projected_spend"],
                remaining=ev["remaining"],
                period=b.period,
                threshold_status=ev["threshold_status"],
                threshold_percentages=b.threshold_percentages or [50, 75, 90, 100],
                thresholds_reached=ev["thresholds_reached"],
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
        )

    return CostBudgetListResponse(
        budgets=out_budgets,
        total=len(out_budgets),
    )


# ---------------------------------------------------------------------------
# POST /cost/budgets
# ---------------------------------------------------------------------------


@router.post(
    "/budgets",
    response_model=CostBudgetItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new FinOps cost budget",
)
async def create_cost_budget(
    payload: CostBudgetPayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostBudgetItem:
    b = await crud_cost.create_budget(db, user_id=current_user.id, data=payload.model_dump())
    current_spend = await crud_cost.calculate_budget_spend(
        db,
        user_id=current_user.id,
        provider=b.provider,
        service=b.service,
        environment=b.environment,
    )
    projected_spend = round(current_spend * 1.05, 2)
    ev = evaluate_budget(b.amount, current_spend, projected_spend)

    return CostBudgetItem(
        id=b.id,
        name=b.name,
        provider=b.provider,
        service=b.service,
        environment=b.environment,
        amount=b.amount,
        current_spend=ev["current_spend"],
        utilization_pct=ev["utilization_pct"],
        projected_spend=ev["projected_spend"],
        remaining=ev["remaining"],
        period=b.period,
        threshold_status=ev["threshold_status"],
        threshold_percentages=b.threshold_percentages,
        thresholds_reached=ev["thresholds_reached"],
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


# ---------------------------------------------------------------------------
# PUT /cost/budgets/{id}
# ---------------------------------------------------------------------------


@router.put(
    "/budgets/{budget_id}",
    response_model=CostBudgetItem,
    summary="Update existing budget parameters",
)
async def update_cost_budget(
    budget_id: uuid.UUID,
    payload: CostBudgetPayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostBudgetItem:
    updated = await crud_cost.update_budget(
        db, user_id=current_user.id, budget_id=budget_id, data=payload.model_dump()
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FinOps budget not found",
        )
    current_spend = await crud_cost.calculate_budget_spend(
        db,
        user_id=current_user.id,
        provider=updated.provider,
        service=updated.service,
        environment=updated.environment,
    )
    projected_spend = round(current_spend * 1.05, 2)
    ev = evaluate_budget(updated.amount, current_spend, projected_spend)

    return CostBudgetItem(
        id=updated.id,
        name=updated.name,
        provider=updated.provider,
        service=updated.service,
        environment=updated.environment,
        amount=updated.amount,
        current_spend=ev["current_spend"],
        utilization_pct=ev["utilization_pct"],
        projected_spend=ev["projected_spend"],
        remaining=ev["remaining"],
        period=updated.period,
        threshold_status=ev["threshold_status"],
        threshold_percentages=updated.threshold_percentages,
        thresholds_reached=ev["thresholds_reached"],
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


# ---------------------------------------------------------------------------
# GET /cost/recommendations & /cost/optimization
# ---------------------------------------------------------------------------


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="List AI optimization recommendations",
)
@router.get(
    "/optimization",
    response_model=RecommendationsResponse,
    summary="List optimization opportunities and waste detection findings",
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
# GET /cost/savings
# ---------------------------------------------------------------------------


@router.get(
    "/savings",
    response_model=CostSavingsResponse,
    summary="Get monthly and annual estimated savings opportunities",
)
async def get_cost_savings(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostSavingsResponse:
    items, _ = await crud_cost.get_recommendations(db, user_id=current_user.id, status="active")
    recs_dicts = [{"estimated_savings": r.estimated_savings, "status": r.status} for r in items]
    summary = calculate_savings_summary(recs_dicts)
    return CostSavingsResponse(**summary)


# ---------------------------------------------------------------------------
# POST /cost/analyze
# ---------------------------------------------------------------------------


@router.post(
    "/analyze",
    response_model=CostAnalyzeResponse,
    summary="Trigger Gemini AI / Local FinOps cost analysis",
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
        analysis_engine=analysis.get("analysis_engine", "Local FinOps Intelligence"),
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
    provider: str | None = None,
    region: str | None = None,
    environment: str | None = None,
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
        provider=provider,
        region=region,
        environment=environment,
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
