"""
Enterprise Service Reliability Engine & SLO Intelligence 2.0 REST API Endpoints.
"""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.reliability import (
    DependencyImpactResponse,
    ErrorBudgetOverviewResponse,
    MultiWindowBurnRateItem,
    ReliabilityAnalyzeResponse,
    ReliabilityIncidentResponse,
    ReliabilityOverviewResponse,
    ReliabilityRecommendationResponse,
    ReliabilityRiskResponse,
    ServiceDetailResponse,
    ServiceReliabilityResponse,
    SloForecastResponse,
)
from app.services import service_reliability_engine
from app.services.slo import fixture_telemetry

log = structlog.get_logger(__name__)
router = APIRouter()


# Helper to get evaluated service profiles
def _get_evaluated_profiles(
    provider: str | None = None,
    service: str | None = None,
    status_filter: str | None = None,
) -> list[dict[str, Any]]:
    items = fixture_telemetry.get_fixture_telemetry(service if service and service != "ALL" else None)
    evals = [service_reliability_engine.evaluate_service_profile(t) for t in items]

    if provider and provider.upper() != "ALL":
        evals = [e for e in evals if e.get("provider", "AWS").upper() == provider.upper()]
    if status_filter and status_filter.upper() != "ALL":
        evals = [e for e in evals if e.get("status", "HEALTHY").upper() == status_filter.upper()]

    return evals


# ── 1. GET /reliability/overview ─────────────────────────────────────────────


@router.get(
    "/overview",
    response_model=ReliabilityOverviewResponse,
    summary="Get overall Service Reliability Engine platform metrics overview",
)
async def get_reliability_overview(
    current_user: User = Depends(require_active_user),
) -> ReliabilityOverviewResponse:
    evals = _get_evaluated_profiles()
    healthy = sum(1 for e in evals if e["status"] == "HEALTHY")
    at_risk = sum(1 for e in evals if e["status"] == "AT_RISK")
    breached = sum(1 for e in evals if e["status"] in ("BREACHING", "BREACHED"))
    avg_score = round(sum(e["reliability_score"] for e in evals) / max(1, len(evals)), 1)
    avg_rem_budget = round(sum(e["error_budget_remaining_pct"] for e in evals) / max(1, len(evals)), 1)
    crit_burns = sum(1 for e in evals if e["burn_rate"] > 3.0)

    return ReliabilityOverviewResponse(
        overall_reliability_score=avg_score,
        services_healthy=healthy,
        services_at_risk=at_risk,
        services_breached=breached,
        slo_compliance_pct=round((healthy / max(1, len(evals))) * 100.0, 1),
        critical_burn_rates_count=crit_burns,
        error_budget_remaining_pct=avg_rem_budget,
        mode_indicator="LOCAL FIXTURE TELEMETRY MODE",
    )


# ── 2. GET /reliability/services ─────────────────────────────────────────────


@router.get(
    "/services",
    response_model=list[ServiceReliabilityResponse],
    summary="List evaluated service reliability profiles",
)
async def list_service_reliability(
    provider: str | None = Query(None, description="Filter by cloud provider"),
    service: str | None = Query(None, description="Filter by service name"),
    status: str | None = Query(None, description="Filter by status (HEALTHY, AT_RISK, BREACHING, BREACHED)"),
    current_user: User = Depends(require_active_user),
) -> list[ServiceReliabilityResponse]:
    evals = _get_evaluated_profiles(provider=provider, service=service, status_filter=status)
    return [ServiceReliabilityResponse(**e) for e in evals]


# ── 3. GET /reliability/services/{service_id} ─────────────────────────


@router.get(
    "/services/{service_id}",
    response_model=ServiceDetailResponse,
    summary="Get comprehensive detail view for a specific service",
)
async def get_service_reliability_detail(
    service_id: str,
    current_user: User = Depends(require_active_user),
) -> ServiceDetailResponse:
    items = fixture_telemetry.get_fixture_telemetry(service_id)
    if not items:
        # Fallback single profile if not found
        t = {
            "service": service_id,
            "provider": "AWS",
            "region": "us-east-1",
            "target_slo": 99.9,
            "availability_pct": 99.95,
            "error_rate_pct": 0.05,
            "latency_p95_ms": 45.0,
            "latency_p99_ms": 110.0,
            "throughput_rps": 250.0,
            "status": "HEALTHY",
        }
    else:
        t = items[0]

    e = service_reliability_engine.evaluate_service_profile(t)
    prof = ServiceReliabilityResponse(**e)

    eb = ErrorBudgetOverviewResponse(
        service_name=e["service_name"],
        target_slo=e["slo_target"],
        total_budget_sec=e["error_budget_total_sec"],
        consumed_budget_sec=e["error_budget_total_sec"] * (e["error_budget_consumed_pct"] / 100.0),
        remaining_budget_sec=e["error_budget_remaining_sec"],
        consumed_budget_pct=e["error_budget_consumed_pct"],
        remaining_budget_pct=e["error_budget_remaining_pct"],
        burn_rate_multiplier=e["burn_rate"],
        status=e["status"],
    )

    mw = {
        k: MultiWindowBurnRateItem(**v)
        for k, v in e["multi_window_burn_rates"].items()
    }

    fc_data = service_reliability_engine.forecast_service_slo(
        target_slo=e["slo_target"],
        current_availability_pct=e["availability_pct"],
        remaining_budget_pct=e["error_budget_remaining_pct"],
        burn_rate_x=e["burn_rate"],
    )
    fc = SloForecastResponse(**fc_data)

    deps = DependencyImpactResponse(
        service_name=e["service_name"],
        upstream_dependencies=["api-gateway", "auth-service"] if service_id != "api-gateway" else [],
        downstream_dependencies=["postgresql-primary", "redis-cache"] if service_id != "redis-cache" else [],
        dependency_health="HEALTHY" if e["status"] == "HEALTHY" else "DEGRADED",
        dependency_correlation=f"Upstream latency correlated with {service_id} query execution time.",
    )

    incs = []
    if e["status"] in ("BREACHED", "BREACHING", "AT_RISK"):
        incs.append(
            ReliabilityIncidentResponse(
                incident_id="INC-9482",
                title=f"Reliability degradation on {service_id}",
                service=service_id,
                severity="HIGH" if e["status"] in ("BREACHED", "BREACHING") else "MEDIUM",
                slo_impact=f"Deducted {(100.0 - e['availability_pct']):.2f}% from availability",
                error_budget_impact=f"Consumed {e['error_budget_consumed_pct']}% of error budget",
                duration_minutes=35,
                status="INVESTIGATING",
            )
        )

    recs_list = service_reliability_engine.generate_reliability_recommendations([e])
    recs = [ReliabilityRecommendationResponse(**r) for r in recs_list]

    return ServiceDetailResponse(
        profile=prof,
        error_budget=eb,
        multi_window_burn_rates=mw,
        forecast=fc,
        dependencies=deps,
        incidents=incs,
        anomalies_count=1 if e["status"] != "HEALTHY" else 0,
        capacity_risk="MEDIUM" if e["status"] in ("BREACHED", "BREACHING") else "LOW",
        security_risk_score=18.0 if e["status"] != "HEALTHY" else 8.0,
        cost_impact_monthly=1450.0 if e["status"] != "HEALTHY" else 450.0,
        recommendations=recs,
    )


# ── 4. GET /reliability/slo ───────────────────────────────────────────────────


@router.get(
    "/slo",
    response_model=list[dict[str, Any]],
    summary="Get SLO targets, actual compliance, and trends across all services",
)
async def get_slo_compliance(
    current_user: User = Depends(require_active_user),
) -> list[dict[str, Any]]:
    evals = _get_evaluated_profiles()
    return [
        {
            "service": e["service_name"],
            "provider": e["provider"],
            "slo_target": e["slo_target"],
            "actual_slo": e["availability_pct"],
            "difference": round(e["availability_pct"] - e["slo_target"], 2),
            "status": e["status"],
            "trend": "IMPROVING" if e["availability_pct"] >= e["slo_target"] else "DEGRADING",
        }
        for e in evals
    ]


# ── 5. GET /reliability/error-budget ─────────────────────────────────────────


@router.get(
    "/error-budget",
    response_model=list[ErrorBudgetOverviewResponse],
    summary="Get error budget totals, remaining percentages, and consumption",
)
async def get_error_budgets(
    current_user: User = Depends(require_active_user),
) -> list[ErrorBudgetOverviewResponse]:
    evals = _get_evaluated_profiles()
    return [
        ErrorBudgetOverviewResponse(
            service_name=e["service_name"],
            target_slo=e["slo_target"],
            total_budget_sec=e["error_budget_total_sec"],
            consumed_budget_sec=round(e["error_budget_total_sec"] * (e["error_budget_consumed_pct"] / 100.0), 1),
            remaining_budget_sec=e["error_budget_remaining_sec"],
            consumed_budget_pct=e["error_budget_consumed_pct"],
            remaining_budget_pct=e["error_budget_remaining_pct"],
            burn_rate_multiplier=e["burn_rate"],
            status=e["status"],
        )
        for e in evals
    ]


# ── 6. GET /reliability/burn-rate ─────────────────────────────────────────────


@router.get(
    "/burn-rate",
    response_model=list[dict[str, Any]],
    summary="Get multi-window burn rates across 5m, 30m, 1h, 6h, 24h, 7d",
)
async def get_burn_rates(
    current_user: User = Depends(require_active_user),
) -> list[dict[str, Any]]:
    evals = _get_evaluated_profiles()
    return [
        {
            "service": e["service_name"],
            "base_burn_rate_x": e["burn_rate"],
            "multi_window_burn_rates": e["multi_window_burn_rates"],
        }
        for e in evals
    ]


# ── 7. GET /reliability/risks ──────────────────────────────────────────────────


@router.get(
    "/risks",
    response_model=list[ReliabilityRiskResponse],
    summary="Get reliability risk evaluation and top factors per service",
)
async def get_reliability_risks(
    current_user: User = Depends(require_active_user),
) -> list[ReliabilityRiskResponse]:
    evals = _get_evaluated_profiles()
    return [
        ReliabilityRiskResponse(
            service_name=e["service_name"],
            risk_score=e["risk_score"],
            risk_level=e["risk_level"],
            top_factors=e["risk_factors"],
        )
        for e in evals
    ]


# ── 8. GET /reliability/forecast ───────────────────────────────────────────────


@router.get(
    "/forecast",
    response_model=list[dict[str, Any]],
    summary="Get deterministic SLO forecasting and projected breach dates",
)
async def get_reliability_forecast(
    current_user: User = Depends(require_active_user),
) -> list[dict[str, Any]]:
    evals = _get_evaluated_profiles()
    res = []
    for e in evals:
        fc = service_reliability_engine.forecast_service_slo(
            target_slo=e["slo_target"],
            current_availability_pct=e["availability_pct"],
            remaining_budget_pct=e["error_budget_remaining_pct"],
            burn_rate_x=e["burn_rate"],
        )
        fc["service"] = e["service_name"]
        res.append(fc)
    return res


# ── 9. GET /reliability/dependencies ──────────────────────────────────────────


@router.get(
    "/dependencies",
    response_model=list[DependencyImpactResponse],
    summary="Get upstream and downstream dependency reliability correlation",
)
async def get_dependency_reliability(
    current_user: User = Depends(require_active_user),
) -> list[DependencyImpactResponse]:
    evals = _get_evaluated_profiles()
    res = []
    for e in evals:
        svc = e["service_name"]
        res.append(
            DependencyImpactResponse(
                service_name=svc,
                upstream_dependencies=["api-gateway"] if svc != "api-gateway" else [],
                downstream_dependencies=["postgresql-primary", "redis-cache"] if svc != "redis-cache" else [],
                dependency_health="HEALTHY" if e["status"] == "HEALTHY" else "DEGRADED",
                dependency_correlation=f"Upstream latency correlated with {svc} query execution time.",
            )
        )
    return res


# ── 10. GET /reliability/incidents ─────────────────────────────────────────────


@router.get(
    "/incidents",
    response_model=list[ReliabilityIncidentResponse],
    summary="Get correlated reliability events and active incident impacts",
)
async def get_reliability_incidents(
    current_user: User = Depends(require_active_user),
) -> list[ReliabilityIncidentResponse]:
    evals = _get_evaluated_profiles()
    res = []
    for e in evals:
        if e["status"] in ("BREACHED", "BREACHING", "AT_RISK"):
            res.append(
                ReliabilityIncidentResponse(
                    incident_id="INC-9482",
                    title=f"Reliability degradation on {e['service_name']}",
                    service=e["service_name"],
                    severity="HIGH" if e["status"] in ("BREACHED", "BREACHING") else "MEDIUM",
                    slo_impact=f"Deducted {(100.0 - e['availability_pct']):.2f}% from availability",
                    error_budget_impact=f"Consumed {e['error_budget_consumed_pct']}% of error budget",
                    duration_minutes=42,
                    status="INVESTIGATING",
                )
            )
    return res


# ── 11. GET /reliability/recommendations ───────────────────────────────────────


@router.get(
    "/recommendations",
    response_model=list[ReliabilityRecommendationResponse],
    summary="Get actionable SRE reliability recommendations",
)
async def get_reliability_recommendations(
    current_user: User = Depends(require_active_user),
) -> list[ReliabilityRecommendationResponse]:
    evals = _get_evaluated_profiles()
    recs_data = service_reliability_engine.generate_reliability_recommendations(evals)
    return [ReliabilityRecommendationResponse(**r) for r in recs_data]


# ── 12. POST /reliability/analyze ─────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=ReliabilityAnalyzeResponse,
    summary="Trigger AI or local reliability intelligence analysis",
)
async def analyze_reliability(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_active_user),
) -> ReliabilityAnalyzeResponse:
    evals = _get_evaluated_profiles()
    result = await service_reliability_engine.analyze_reliability_ai(
        db,
        user_id=str(current_user.id),
        services_evals=evals,
    )
    return ReliabilityAnalyzeResponse(**result)
