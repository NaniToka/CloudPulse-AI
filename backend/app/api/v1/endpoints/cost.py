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
from datetime import datetime
from typing import Any

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
    CostDriversResponse,
    CostExplorerNode,
    CostExplorerResponse,
    CostForecastResponse,
    CostHealthScoreResponse,
    CostOverviewResponse,
    CostSavingsResponse,
    CostTrendsResponse,
    DailyCostItem,
    ExecutiveCostSummaryResponse,
    FinOpsReportRequest,
    FinOpsReportResponse,
    PeriodComparisonResponse,
    ProviderCostItem,
    ProviderCostsResponse,
    RecommendationItem,
    RecommendationsResponse,
    RegionCostItem,
    RegionCostsResponse,
    SavingsCenterResponse,
    ServiceCostItem,
    ServiceCostsResponse,
)
from app.services.cost_ai_service import analyze_cloud_costs_with_gemini
from app.services.cost_engine import (
    analyze_cost_drivers,
    calculate_cost_forecast,
    calculate_finops_health_score,
    calculate_period_comparison,
    calculate_savings_center_breakdown,
    calculate_savings_summary,
    detect_cost_anomalies,
    evaluate_budget,
    generate_executive_cost_summary,
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
    provider: str | None = Query(None, description="Filter by cloud provider (aws, azure, gcp, kubernetes)"),
    date_range: str | None = Query(None, description="Date range (7_days, 30_days, quarter)"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostOverviewResponse:
    log.info("get_cost_overview", user_id=str(current_user.id), provider=provider, date_range=date_range)
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id, provider=provider, date_range=date_range)
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=200)

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
        data_source="Demo Data — Local Development",
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
    provider: str | None = Query(None, description="Filter by cloud provider"),
    date_range: str | None = Query(None, description="Date range filter"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostTrendsResponse:
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id, provider=provider, date_range=date_range)
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
    provider: str | None = Query(None, description="Filter by cloud provider"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProviderCostsResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    resources_dicts = [
        {"cost": c.cost, "provider": c.provider, "service": c.service} for c in costs
    ]
    providers = [ProviderCostItem(**p) for p in group_costs_by_provider(resources_dicts)]
    total = round(sum(p.cost for p in providers), 2)

    return ProviderCostsResponse(
        providers=providers,
        total_cost=total,
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
    provider: str | None = Query(None, description="Filter by cloud provider"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceCostsResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    resources_dicts = [{"cost": c.cost, "service": c.service} for c in costs]
    services = [ServiceCostItem(**s) for s in group_costs_by_service(resources_dicts)]
    total = round(sum(s.cost for s in services), 2)

    return ServiceCostsResponse(
        services=services,
        total_cost=total,
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
    provider: str | None = Query(None, description="Filter by cloud provider"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> RegionCostsResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    resources_dicts = [{"cost": c.cost, "region": c.region} for c in costs]
    regions = [RegionCostItem(**r) for r in group_costs_by_region(resources_dicts)]
    total = round(sum(r.cost for r in regions), 2)

    return RegionCostsResponse(
        regions=regions,
        total_cost=total,
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
    provider: str | None = Query(None, description="Filter by cloud provider"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostAnomaliesResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
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
    provider: str | None = Query(None, description="Filter by cloud provider"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostForecastResponse:
    data = await crud_cost.get_cost_overview_data(db, user_id=current_user.id, provider=provider)
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


# ---------------------------------------------------------------------------
# Executive FinOps Intelligence Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/health-score",
    response_model=CostHealthScoreResponse,
    summary="Get deterministic FinOps Health Score and posture factors",
)
async def get_cost_health_score(
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostHealthScoreResponse:
    overview = await crud_cost.get_cost_overview_data(db, user_id=current_user.id, provider=provider)
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    resources_dicts = [{"cost": c.cost, "status": c.status, "resource_name": c.resource_name, "service": c.service, "provider": c.provider} for c in costs]
    anomalies = detect_cost_anomalies(resources_dicts)
    crit_count = sum(1 for a in anomalies if a["severity"] == "CRITICAL")
    budgets_db = await crud_cost.get_budgets(db, user_id=current_user.id)
    tot_budget = sum(b.amount for b in budgets_db) if budgets_db else 0.0
    budget_ev = evaluate_budget(tot_budget, overview["monthly_cost"], overview["projected_cost"])

    score_data = calculate_finops_health_score(
        monthly_cost=overview["monthly_cost"],
        potential_savings=overview["potential_savings"],
        anomalies_count=len(anomalies),
        critical_anomalies_count=crit_count,
        budget_utilization_pct=budget_ev["utilization_pct"],
        projected_variance_pct=abs(overview["percentage_change"]),
    )
    return CostHealthScoreResponse(**score_data)


@router.get(
    "/executive-summary",
    response_model=ExecutiveCostSummaryResponse,
    summary="Get data-derived executive intelligence statements",
)
async def get_executive_cost_summary(
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveCostSummaryResponse:
    overview = await crud_cost.get_cost_overview_data(db, user_id=current_user.id, provider=provider)
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    recs, _ = await crud_cost.get_recommendations(db, user_id=current_user.id, status="active")
    resources_dicts = [{"cost": c.cost, "status": c.status, "resource_name": c.resource_name, "service": c.service, "provider": c.provider} for c in costs]
    recs_dicts = [{"estimated_savings": r.estimated_savings, "status": r.status} for r in recs]
    anomalies = detect_cost_anomalies(resources_dicts)

    summary = generate_executive_cost_summary(
        monthly_cost=overview["monthly_cost"],
        previous_month_cost=overview["previous_month_cost"],
        percentage_change=overview["percentage_change"],
        service_breakdown=overview["service_breakdown"],
        recommendations=recs_dicts,
        anomalies=anomalies,
    )
    return ExecutiveCostSummaryResponse(**summary)


@router.get(
    "/drivers",
    response_model=CostDriversResponse,
    summary="Identify major cost drivers with values and explicit reasons",
)
async def get_cost_drivers(
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostDriversResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    recs, _ = await crud_cost.get_recommendations(db, user_id=current_user.id, status="active")
    resources_dicts = [{"cost": c.cost, "status": c.status, "resource_name": c.resource_name, "service": c.service, "provider": c.provider} for c in costs]
    recs_dicts = [{"title": r.title, "description": r.description, "estimated_savings": r.estimated_savings, "status": r.status} for r in recs]
    anomalies = detect_cost_anomalies(resources_dicts)

    drivers = analyze_cost_drivers(resources_dicts, anomalies, recs_dicts)
    return CostDriversResponse(**drivers)


@router.get(
    "/period-comparison",
    response_model=PeriodComparisonResponse,
    summary="Compare current vs previous period spend and changes across providers & services",
)
async def get_period_comparison(
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PeriodComparisonResponse:
    overview = await crud_cost.get_cost_overview_data(db, user_id=current_user.id, provider=provider)
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=300)
    resources_dicts = [{"cost": c.cost, "provider": c.provider, "service": c.service} for c in costs]

    comparison = calculate_period_comparison(resources_dicts, overview["previous_month_cost"])
    return PeriodComparisonResponse(**comparison)


@router.get(
    "/explorer",
    response_model=CostExplorerResponse,
    summary="Hierarchical tree drill-down cost explorer (Provider -> Service -> Region -> Resource)",
)
async def get_cost_explorer(
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CostExplorerResponse:
    costs, _ = await crud_cost.get_costs(db, user_id=current_user.id, provider=provider, limit=500)
    total_cost = round(sum(c.cost for c in costs), 2)

    # Build hierarchical tree: Provider -> Service -> Region -> Resource
    tree: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {}

    for c in costs:
        p_name = c.provider.upper()
        s_name = c.service
        r_name = c.region

        if p_name not in tree:
            tree[p_name] = {}
        if s_name not in tree[p_name]:
            tree[p_name][s_name] = {}
        if r_name not in tree[p_name][s_name]:
            tree[p_name][s_name][r_name] = []

        tree[p_name][s_name][r_name].append(
            {
                "id": str(c.id),
                "name": c.resource_name,
                "level": "resource",
                "cost": round(c.cost, 2),
                "percentage_of_total": round((c.cost / total_cost * 100.0), 1) if total_cost > 0 else 0.0,
                "resource_count": 1,
                "children": [],
            }
        )

    provider_nodes = []
    for p_name, services in tree.items():
        p_cost = sum(r["cost"] for s in services.values() for reg in s.values() for r in reg)
        p_pct = round((p_cost / total_cost * 100.0), 1) if total_cost > 0 else 0.0

        service_nodes = []
        for s_name, regions in services.items():
            s_cost = sum(r["cost"] for reg in regions.values() for r in reg)
            s_pct = round((s_cost / total_cost * 100.0), 1) if total_cost > 0 else 0.0

            region_nodes = []
            for r_name, res_list in regions.items():
                reg_cost = sum(r["cost"] for r in res_list)
                reg_pct = round((reg_cost / total_cost * 100.0), 1) if total_cost > 0 else 0.0

                region_nodes.append(
                    CostExplorerNode(
                        id=f"reg-{p_name}-{s_name}-{r_name}",
                        name=r_name,
                        level="region",
                        cost=round(reg_cost, 2),
                        percentage_of_total=reg_pct,
                        resource_count=len(res_list),
                        children=[CostExplorerNode(**r) for r in res_list],
                    )
                )

            service_nodes.append(
                CostExplorerNode(
                    id=f"svc-{p_name}-{s_name}",
                    name=s_name,
                    level="service",
                    cost=round(s_cost, 2),
                    percentage_of_total=s_pct,
                    resource_count=sum(len(res) for res in regions.values()),
                    children=region_nodes,
                )
            )

        provider_nodes.append(
            CostExplorerNode(
                id=f"prov-{p_name}",
                name=p_name,
                level="provider",
                cost=round(p_cost, 2),
                percentage_of_total=p_pct,
                resource_count=sum(len(res) for s in services.values() for res in s.values()),
                children=service_nodes,
            )
        )

    return CostExplorerResponse(nodes=provider_nodes, total_cost=total_cost)


@router.get(
    "/savings-center",
    response_model=SavingsCenterResponse,
    summary="Get complete Savings Center summary and category/provider/service breakdowns",
)
async def get_savings_center(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SavingsCenterResponse:
    recs, _ = await crud_cost.get_recommendations(db, user_id=current_user.id, status="active")
    recs_dicts = [
        {
            "estimated_savings": r.estimated_savings,
            "status": r.status,
            "provider": getattr(r, "provider", "AWS"),
            "recommendation_type": r.recommendation_type,
            "service": r.service,
        }
        for r in recs
    ]
    breakdown = calculate_savings_center_breakdown(recs_dicts)
    return SavingsCenterResponse(**breakdown)


# ---------------------------------------------------------------------------
# FinOps PDF Report & Export Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/reports/generate",
    response_model=FinOpsReportResponse,
    summary="Generate 12-section FinOps Executive Intelligence Report payload",
)
async def generate_finops_report(
    payload: FinOpsReportRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> FinOpsReportResponse:
    from app.services.cost_report_service import generate_finops_executive_report_data

    report_data = await generate_finops_executive_report_data(
        db, user_id=current_user.id, provider=payload.provider, date_range=payload.date_range
    )
    return FinOpsReportResponse(**report_data)


@router.get(
    "/reports/pdf",
    summary="Download downloadable PDF FinOps Executive Intelligence Report",
)
async def download_finops_pdf_report(
    date_range: str = Query("30_days"),
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import Response

    from app.services.cost_report_service import generate_finops_pdf_report

    pdf_bytes = await generate_finops_pdf_report(
        db, user_id=current_user.id, provider=provider, date_range=date_range
    )
    filename = f"FinOps_Executive_Report_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/export",
    summary="Export FinOps cost inventory in CSV or PDF format",
)
async def export_finops_data(
    format_type: str = Query("csv", alias="format"),
    provider: str | None = Query(None),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import Response

    if format_type.lower() == "pdf":
        from app.services.cost_report_service import generate_finops_pdf_report

        pdf_bytes = await generate_finops_pdf_report(db, user_id=current_user.id, provider=provider)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="FinOps_Export.pdf"'},
        )
    else:
        from app.services.cost_report_service import export_finops_csv

        csv_str = await export_finops_csv(db, user_id=current_user.id, provider=provider)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="FinOps_Export.csv"'},
        )

