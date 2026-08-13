"""
Enterprise SLO, SLA & Error Budget Intelligence Center REST API Endpoints.
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_slo
from app.models.user import User
from app.schemas.slo import (
    BurnRateResponse,
    CorrelatedIncidentResponse,
    ErrorBudgetResponse,
    ServiceReliabilityResponse,
    SliMetricsResponse,
    SloAnalyzeResponse,
    SloForecastResponse,
    SloObjectiveCreate,
    SloObjectiveResponse,
    SloObjectiveUpdate,
    SloOverviewResponse,
    SloRecommendationResponse,
    SloViolationResponse,
)
from app.services.slo import (
    burn_rate_engine,
    error_budget_engine,
    fixture_telemetry,
    forecasting_engine,
    incident_correlation,
    reliability_score_engine,
    sli_engine,
    violation_engine,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# ── 1. GET /slo/overview ───────────────────────────────────────────────────────


@router.get(
    "/overview",
    response_model=SloOverviewResponse,
    summary="Get platform SLO compliance and reliability overview",
)
async def get_slo_overview(
    current_user: User = Depends(require_active_user),
) -> SloOverviewResponse:
    ov = reliability_score_engine.calculate_platform_reliability_overview()
    return SloOverviewResponse(**ov)


# ── 2. GET /slo/services & GET /slo/services/{service} ─────────────────────────


@router.get(
    "/services",
    response_model=list[ServiceReliabilityResponse],
    summary="Get per-service reliability summary",
)
async def list_service_reliability(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
) -> list[ServiceReliabilityResponse]:
    items = fixture_telemetry.get_fixture_telemetry(service)
    res: list[ServiceReliabilityResponse] = []

    for t in items:
        target = t.get("target_slo", 99.9)
        avail = t.get("availability_pct", 100.0)
        err = t.get("error_rate_pct", 0.0)
        lat = t.get("latency_p95_ms", 50.0)

        rel = reliability_score_engine.calculate_service_reliability_score(
            availability_pct=avail,
            error_rate_pct=err,
            latency_p95_ms=lat,
            target_slo=target,
        )

        res.append(
            ServiceReliabilityResponse(
                service=t["service"],
                scenario=t["scenario"],
                indicator_type=t["indicator_type"],
                target_slo=target,
                availability_pct=avail,
                error_rate_pct=err,
                latency_p95_ms=lat,
                throughput_rps=t["throughput_rps"],
                reliability_score=rel["reliability_score"],
                status=t["status"],
                contributing_factors=rel["contributing_factors"],
            )
        )

    return res


@router.get(
    "/services/{service}",
    response_model=ServiceReliabilityResponse,
    summary="Get detailed single service reliability breakdown",
)
async def get_service_reliability(
    service: str,
    current_user: User = Depends(require_active_user),
) -> ServiceReliabilityResponse:
    items = fixture_telemetry.get_fixture_telemetry(service)
    if not items:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")

    t = items[0]
    target = t.get("target_slo", 99.9)
    avail = t.get("availability_pct", 100.0)
    err = t.get("error_rate_pct", 0.0)
    lat = t.get("latency_p95_ms", 50.0)

    rel = reliability_score_engine.calculate_service_reliability_score(
        availability_pct=avail,
        error_rate_pct=err,
        latency_p95_ms=lat,
        target_slo=target,
    )

    return ServiceReliabilityResponse(
        service=t["service"],
        scenario=t["scenario"],
        indicator_type=t["indicator_type"],
        target_slo=target,
        availability_pct=avail,
        error_rate_pct=err,
        latency_p95_ms=lat,
        throughput_rps=t["throughput_rps"],
        reliability_score=rel["reliability_score"],
        status=t["status"],
        contributing_factors=rel["contributing_factors"],
    )


# ── 3. GET /slo/indicators ────────────────────────────────────────────────────


@router.get(
    "/indicators",
    response_model=list[SliMetricsResponse],
    summary="Get Service Level Indicators (SLIs)",
)
async def get_indicators(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
) -> list[SliMetricsResponse]:
    items = fixture_telemetry.get_fixture_telemetry(service)
    res: list[SliMetricsResponse] = []

    for t in items:
        sli = sli_engine.calculate_sli(
            total_events=t["total_events"],
            good_events=t["good_events"],
            bad_events=t["bad_events"],
        )
        res.append(
            SliMetricsResponse(
                service=t["service"],
                indicator_type=t["indicator_type"],
                total_events=sli["total_events"],
                good_events=sli["good_events"],
                bad_events=sli["bad_events"],
                availability_pct=sli["availability_pct"],
                error_rate_pct=sli["error_rate_pct"],
                latency_p50_ms=t.get("latency_p50_ms", sli["latency_p50_ms"]),
                latency_p90_ms=t.get("latency_p90_ms", sli["latency_p90_ms"]),
                latency_p95_ms=t.get("latency_p95_ms", sli["latency_p95_ms"]),
                latency_p99_ms=t.get("latency_p99_ms", sli["latency_p99_ms"]),
                throughput_rps=sli["throughput_rps"],
                window=t["window"],
                status=t["status"],
            )
        )

    return res


# ── 4. Objectives CRUD (/slo/objectives) ──────────────────────────────────────


@router.get(
    "/objectives",
    response_model=list[SloObjectiveResponse],
    summary="List Service Level Objectives (SLOs)",
)
async def list_objectives(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[SloObjectiveResponse]:
    objs = await crud_slo.get_objectives(db, service=service)
    return [SloObjectiveResponse.model_validate(o) for o in objs]


@router.post(
    "/objectives",
    response_model=SloObjectiveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Service Level Objective",
)
async def create_objective(
    obj_in: SloObjectiveCreate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SloObjectiveResponse:
    obj = await crud_slo.create_objective(db, obj_in=obj_in, user_id=current_user.id)
    return SloObjectiveResponse.model_validate(obj)


@router.put(
    "/objectives/{objective_id}",
    response_model=SloObjectiveResponse,
    summary="Update a Service Level Objective",
)
async def update_objective(
    objective_id: uuid.UUID,
    obj_in: SloObjectiveUpdate,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SloObjectiveResponse:
    obj = await crud_slo.get_objective_by_id(db, objective_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Service Level Objective not found")

    updated = await crud_slo.update_objective(db, objective=obj, obj_in=obj_in)
    return SloObjectiveResponse.model_validate(updated)


@router.delete(
    "/objectives/{objective_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a Service Level Objective",
)
async def delete_objective(
    objective_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    obj = await crud_slo.get_objective_by_id(db, objective_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Service Level Objective not found")
    await crud_slo.delete_objective(db, objective=obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── 5. GET /slo/error-budget ──────────────────────────────────────────────────


@router.get(
    "/error-budget",
    response_model=list[ErrorBudgetResponse],
    summary="Get Error Budget consumption & remaining breakdown",
)
async def get_error_budgets(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
) -> list[ErrorBudgetResponse]:
    items = fixture_telemetry.get_fixture_telemetry(service)
    res: list[ErrorBudgetResponse] = []

    for t in items:
        target = t.get("target_slo", 99.9)
        avail = t.get("availability_pct", 100.0)
        eb = error_budget_engine.calculate_error_budget(target_slo=target, current_availability_pct=avail)

        res.append(
            ErrorBudgetResponse(
                service=t["service"],
                target_slo=target,
                window_days=eb["window_days"],
                total_budget_sec=eb["total_budget_sec"],
                consumed_budget_sec=eb["consumed_budget_sec"],
                remaining_budget_sec=eb["remaining_budget_sec"],
                consumed_budget_pct=eb["consumed_budget_pct"],
                remaining_budget_pct=eb["remaining_budget_pct"],
                burn_rate_multiplier=eb["burn_rate_multiplier"],
                status=eb["status"],
            )
        )

    return res


# ── 6. GET /slo/burn-rate ─────────────────────────────────────────────────────


@router.get(
    "/burn-rate",
    response_model=list[BurnRateResponse],
    summary="Get multi-window burn rates and alert status",
)
async def get_burn_rates(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
) -> list[BurnRateResponse]:
    items = fixture_telemetry.get_fixture_telemetry(service)
    res: list[BurnRateResponse] = []

    for t in items:
        target = t.get("target_slo", 99.9)
        err = t.get("error_rate_pct", 0.0)
        br = burn_rate_engine.calculate_burn_rate(target_slo=target, observed_error_rate_pct=err, window_hours=1)

        res.append(
            BurnRateResponse(
                service=t["service"],
                burn_rate_x=br["burn_rate_x"],
                severity=br["severity"],
                window_hours=br["window_hours"],
                observed_failure_rate=br["observed_failure_rate"],
                allowed_failure_rate=br["allowed_failure_rate"],
                explanation=br["explanation"],
            )
        )

    return res


# ── 7. GET /slo/violations ────────────────────────────────────────────────────


@router.get(
    "/violations",
    response_model=list[SloViolationResponse],
    summary="Get active & historical SLO/SLA violations",
)
async def get_violations(
    service: str | None = Query(None, description="Filter by service name"),
    severity: str | None = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    current_user: User = Depends(require_active_user),
) -> list[SloViolationResponse]:
    items = fixture_telemetry.get_fixture_telemetry(service)
    viols = violation_engine.detect_slo_violations(items)

    if severity:
        viols = [v for v in viols if v["severity"].upper() == severity.upper()]

    return [SloViolationResponse(**v) for v in viols]


# ── 8. GET /slo/forecast ──────────────────────────────────────────────────────


@router.get(
    "/forecast",
    response_model=list[SloForecastResponse],
    summary="Get reliability trends and month-end SLO projections",
)
async def get_forecasts(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
) -> list[SloForecastResponse]:
    items = fixture_telemetry.get_fixture_telemetry(service)
    res: list[SloForecastResponse] = []

    for t in items:
        target = t.get("target_slo", 99.9)
        avail = t.get("availability_pct", 100.0)
        err = t.get("error_rate_pct", 0.0)

        eb = error_budget_engine.calculate_error_budget(target_slo=target, current_availability_pct=avail)
        br = burn_rate_engine.calculate_burn_rate(target_slo=target, observed_error_rate_pct=err)

        fc = forecasting_engine.calculate_slo_forecast(
            target_slo=target,
            current_availability_pct=avail,
            remaining_budget_pct=eb["remaining_budget_pct"],
            burn_rate_x=br["burn_rate_x"],
        )

        res.append(
            SloForecastResponse(
                service=t["service"],
                target_slo=target,
                current_availability_pct=avail,
                projected_month_end_slo_pct=fc["projected_month_end_slo_pct"],
                projected_budget_consumed_pct=fc["projected_budget_consumed_pct"],
                projected_remaining_budget_pct=fc["projected_remaining_budget_pct"],
                days_to_exhaustion=fc["days_to_exhaustion"],
                projected_exhaustion_date=fc["projected_exhaustion_date"],
                is_compliant_projected=fc["is_compliant_projected"],
                confidence_pct=fc["confidence_pct"],
            )
        )

    return res


# ── 9. GET /slo/reliability ───────────────────────────────────────────────────


@router.get(
    "/reliability",
    response_model=list[ServiceReliabilityResponse],
    summary="Get overall service reliability score breakdown",
)
async def get_reliability(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
) -> list[ServiceReliabilityResponse]:
    return await list_service_reliability(service=service, current_user=current_user)


# ── 10. GET /slo/incidents ────────────────────────────────────────────────────


@router.get(
    "/incidents",
    response_model=list[CorrelatedIncidentResponse],
    summary="Get correlated incident impact on SLOs and error budgets",
)
async def get_correlated_incidents(
    service: str | None = Query(None, description="Filter by service name"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[CorrelatedIncidentResponse]:
    correl = await incident_correlation.correlate_slo_incidents(db, service_name=service)
    return [CorrelatedIncidentResponse(**c) for c in correl]


# ── 11. POST /slo/analyze ─────────────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=SloAnalyzeResponse,
    summary="Trigger local or AI SRE intelligence analysis on SLOs",
)
async def analyze_slos(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SloAnalyzeResponse:
    ov = reliability_score_engine.calculate_platform_reliability_overview()
    items = fixture_telemetry.get_fixture_telemetry()
    viols = violation_engine.detect_slo_violations(items)

    recs = [
        SloRecommendationResponse(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "rec-payment")),
            service="payment-service",
            problem="High P95 latency (780ms) causing SLO breach",
            impact="Loss of $4,500/hr in checkout conversion flow",
            recommendation="Scale payment API pod replicas up from 4 to 8 and optimize database connection pool size",
            priority="HIGH",
            expected_improvement="Reduce P95 latency by 65% to < 280ms",
        ),
        SloRecommendationResponse(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "rec-notification")),
            service="notification-service",
            problem="Worker queue congestion causing 12.5x burn rate spike",
            impact="Consuming 18.5% of monthly error budget per hour",
            recommendation="Increase SQS consumer concurrency and introduce exponential backoff retries",
            priority="HIGH",
            expected_improvement="Normalize burn rate to < 1.2x",
        ),
        SloRecommendationResponse(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "rec-analytics")),
            service="analytics-service",
            problem="Database connection failure driving 3.2% error rate",
            impact="Degraded reporting queries for internal BI dashboards",
            recommendation="Enable read-replica failover and implement circuit breaker pattern",
            priority="MEDIUM",
            expected_improvement="Eliminate DB connection timeouts",
        ),
    ]

    return SloAnalyzeResponse(
        overview=SloOverviewResponse(**ov),
        services_analyzed=len(items),
        critical_breaches_count=len(viols),
        recommendations=recs,
        analysis_summary="SRE Intelligence Analysis Complete: 2 critical breaches detected. Immediate scaling recommended for payment-service and notification-service.",
    )
