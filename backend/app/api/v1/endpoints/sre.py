"""
Enterprise SRE & Reliability Intelligence Center REST API Endpoints.

Routes:
-------
GET    /api/v1/sre/overview        — Platform reliability score, healthy/at-risk/breach counts
GET    /api/v1/sre/services        — Detailed per-service reliability summary & sorting
GET    /api/v1/sre/services/{name} — Detailed single-service reliability breakdown
GET    /api/v1/sre/slis            — Service Level Indicators (availability, latency, error rate, RPS)
GET    /api/v1/sre/slos            — List configured Service Level Objectives
POST   /api/v1/sre/slos            — Create new Service Level Objective
PUT    /api/v1/sre/slos/{id}       — Update existing Service Level Objective
GET    /api/v1/sre/error-budgets   — Error budget consumption & remaining percentages
GET    /api/v1/sre/burn-rates      — Multi-window burn rate calculations (1h, 6h, 24h, 7d)
GET    /api/v1/sre/reliability     — Overall reliability score breakdown
GET    /api/v1/sre/risks           — Reliability risk detection & warnings
GET    /api/v1/sre/incidents       — Correlated incident impact on SLOs and error budgets
GET    /api/v1/sre/dependencies    — Dependency graph reliability & blast radius impact
GET    /api/v1/sre/forecast        — Predictive 24h, 7d, 30d reliability trends
GET    /api/v1/sre/recommendations — Actionable SRE recovery recommendations
POST   /api/v1/sre/analyze         — Trigger Gemini AI / Local SRE Intelligence analysis
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_sre
from app.models.incident import Incident
from app.models.service_dependency import ServiceDependency, ServiceNode
from app.models.user import User
from app.schemas.sre import (
    BurnRateItem,
    DependencyImpactItem,
    DependencyImpactListResponse,
    ErrorBudgetItem,
    IncidentImpactItem,
    IncidentImpactListResponse,
    ReliabilityForecastResponse,
    ReliabilityRiskItem,
    ReliabilityRiskListResponse,
    ServiceReliabilityItem,
    ServiceReliabilityListResponse,
    SliMetricsItem,
    SloCreatePayload,
    SloItem,
    SloListResponse,
    SloUpdatePayload,
    SreAnalyzeResponse,
    SreOverviewResponse,
    SreRecommendationItem,
    SreRecommendationListResponse,
)
from app.services.sre_ai_service import analyze_reliability_with_gemini
from app.services.sre_engine import (
    calculate_burn_rates,
    calculate_error_budget,
    calculate_reliability_score,
    calculate_sli_metrics,
    detect_reliability_risks,
    evaluate_slo,
    forecast_reliability_trends,
    generate_sre_recommendations,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# Helper to fetch active services with fallback defaults if empty
async def _get_services_data(db: AsyncSession) -> list[dict[str, Any]]:
  stmt = select(ServiceNode).order_by(ServiceNode.name.asc())
  res = await db.execute(stmt)
  nodes = list(res.scalars().all())

  if not nodes:
    # Fixture default services if DB has no ServiceNode records
    return [
        {
            "name": "api-gateway",
            "type": "api",
            "environment": "production",
            "region": "us-east-1",
            "status": "DEGRADED",
            "health_score": 78.5,
            "error_rate": 0.85,
            "latency_p99_ms": 320.0,
            "request_rate": 1450.0,
            "active_incidents_count": 1,
        },
        {
            "name": "auth-service",
            "type": "service",
            "environment": "production",
            "region": "us-east-1",
            "status": "HEALTHY",
            "health_score": 96.0,
            "error_rate": 0.05,
            "latency_p99_ms": 45.0,
            "request_rate": 820.0,
            "active_incidents_count": 0,
        },
        {
            "name": "payment-service",
            "type": "service",
            "environment": "production",
            "region": "us-east-1",
            "status": "DEGRADED",
            "health_score": 82.0,
            "error_rate": 0.45,
            "latency_p99_ms": 520.0,
            "request_rate": 410.0,
            "active_incidents_count": 1,
        },
        {
            "name": "order-service",
            "type": "service",
            "environment": "production",
            "region": "us-east-1",
            "status": "HEALTHY",
            "health_score": 98.0,
            "error_rate": 0.12,
            "latency_p99_ms": 85.0,
            "request_rate": 350.0,
            "active_incidents_count": 0,
        },
        {
            "name": "notification-service",
            "type": "service",
            "environment": "production",
            "region": "us-east-1",
            "status": "HEALTHY",
            "health_score": 99.0,
            "error_rate": 0.02,
            "latency_p99_ms": 60.0,
            "request_rate": 180.0,
            "active_incidents_count": 0,
        },
        {
            "name": "user-service",
            "type": "service",
            "environment": "production",
            "region": "us-east-1",
            "status": "HEALTHY",
            "health_score": 97.5,
            "error_rate": 0.08,
            "latency_p99_ms": 50.0,
            "request_rate": 620.0,
            "active_incidents_count": 0,
        },
    ]

  return [
      {
          "name": n.name,
          "type": n.type,
          "environment": n.environment,
          "region": n.region,
          "status": n.status,
          "health_score": n.health_score,
          "error_rate": n.error_rate,
          "latency_p99_ms": n.latency_p99_ms,
          "request_rate": n.request_rate,
          "active_incidents_count": n.active_incidents_count,
      }
      for n in nodes
  ]


# ---------------------------------------------------------------------------
# GET /sre/overview
# ---------------------------------------------------------------------------


@router.get(
    "/overview",
    response_model=SreOverviewResponse,
    summary="Get overall platform reliability score, status counts, and error budget summary",
)
async def get_sre_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SreOverviewResponse:
  log.info("get_sre_overview", user_id=str(current_user.id))
  services = await _get_services_data(db)
  slos_db = await crud_sre.get_slos(db, user_id=current_user.id)

  healthy_cnt = 0
  at_risk_cnt = 0
  breach_cnt = 0
  total_score = 0.0

  for s in services:
    err_rate = s["error_rate"]
    avail = max(0.0, 100.0 - err_rate)
    lat_p95 = s["latency_p99_ms"] * 0.75

    # Check matching SLO or default 99.9%
    matching_slo = next(
        (slo for slo in slos_db if slo.service == s["name"]), None
    )
    target_slo = matching_slo.target if matching_slo else 99.9

    eb = calculate_error_budget(target_slo, avail)
    burn = calculate_burn_rates(eb, err_rate)
    rel = calculate_reliability_score(
        avail,
        lat_p95,
        err_rate,
        "BREACHED" if avail < target_slo else "HEALTHY",
        burn["status"],
        s["active_incidents_count"],
    )

    total_score += rel["score"]
    if avail < target_slo:
      breach_cnt += 1
    elif eb["remaining_pct"] < 30.0 or burn["status"] == "ELEVATED":
      at_risk_cnt += 1
    else:
      healthy_cnt += 1

  avg_score = (
      round(total_score / max(1, len(services)), 1) if services else 95.0
  )
  rating = (
      "EXCELLENT"
      if avg_score >= 95.0
      else ("GOOD" if avg_score >= 85.0 else "DEGRADED")
  )

  inc_stmt = select(Incident).where(
      Incident.status.in_(["OPEN", "INVESTIGATING", "MITIGATING", "DETECTED"])
  )
  inc_res = await db.execute(inc_stmt)
  active_incidents = len(list(inc_res.scalars().all()))

  return SreOverviewResponse(
      overall_score=avg_score,
      overall_rating=rating,
      services_healthy=healthy_cnt,
      services_at_risk=at_risk_cnt,
      slo_breaches=breach_cnt,
      error_budget_remaining_avg=84.5,
      active_incidents_count=active_incidents,
      data_source="Demo Data — No Production Telemetry Connected",
      environment="Local Development",
  )


# ---------------------------------------------------------------------------
# GET /sre/services & /sre/services/{service_name}
# ---------------------------------------------------------------------------


@router.get(
    "/services",
    response_model=ServiceReliabilityListResponse,
    summary="List per-service SRE reliability metrics with sorting",
)
async def get_service_reliability_list(
    sort_by: str = Query(default="worst_reliability"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceReliabilityListResponse:
  services_raw = await _get_services_data(db)
  slos_db = await crud_sre.get_slos(db, user_id=current_user.id)

  items = []
  for s in services_raw:
    name = s["name"]
    err_rate = s["error_rate"]
    avail = max(0.0, 100.0 - err_rate)
    lat_p95 = round(s["latency_p99_ms"] * 0.75, 1)

    matching_slo = next(
        (slo for slo in slos_db if slo.service == name), None
    )
    target_slo = matching_slo.target if matching_slo else 99.9

    eval_res = evaluate_slo("availability", target_slo, avail)
    eb = calculate_error_budget(target_slo, avail)
    burn = calculate_burn_rates(eb, err_rate)
    rel = calculate_reliability_score(
        avail,
        lat_p95,
        err_rate,
        eval_res["status"],
        burn["status"],
        s["active_incidents_count"],
    )

    items.append(
        ServiceReliabilityItem(
            service=name,
            reliability_score=rel["score"],
            rating=rel["rating"],
            availability=avail,
            latency_p95_ms=lat_p95,
            error_rate=err_rate,
            throughput_rps=s["request_rate"],
            slo_status=eval_res["status"],
            error_budget_remaining_pct=eb["remaining_pct"],
            burn_rate_status=burn["status"],
            active_incidents_count=s["active_incidents_count"],
            trend="DEGRADED" if eval_res["status"] == "BREACHED" else "STABLE",
        )
    )

  # Sorting logic
  if sort_by == "worst_reliability":
    items.sort(key=lambda x: x.reliability_score)
  elif sort_by == "highest_error_rate":
    items.sort(key=lambda x: x.error_rate, reverse=True)
  elif sort_by == "highest_latency":
    items.sort(key=lambda x: x.latency_p95_ms, reverse=True)
  elif sort_by == "highest_burn_rate":
    items.sort(key=lambda x: x.error_budget_remaining_pct)
  elif sort_by == "most_incidents":
    items.sort(key=lambda x: x.active_incidents_count, reverse=True)

  return ServiceReliabilityListResponse(
      services=items,
      total=len(items),
  )


@router.get(
    "/services/{service_name}",
    response_model=ServiceReliabilityItem,
    summary="Get detailed reliability metrics for a specific service",
)
async def get_service_reliability_detail(
    service_name: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceReliabilityItem:
  services_raw = await _get_services_data(db)
  svc = next(
      (s for s in services_raw if s["name"].lower() == service_name.lower()),
      None,
  )

  if not svc:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Service '{service_name}' not found in SRE monitoring.",
    )

  err_rate = svc["error_rate"]
  avail = max(0.0, 100.0 - err_rate)
  lat_p95 = round(svc["latency_p99_ms"] * 0.75, 1)

  slos_db = await crud_sre.get_slos(db, service=svc["name"])
  matching_slo = slos_db[0] if slos_db else None
  target_slo = matching_slo.target if matching_slo else 99.9

  eval_res = evaluate_slo("availability", target_slo, avail)
  eb = calculate_error_budget(target_slo, avail)
  burn = calculate_burn_rates(eb, err_rate)
  rel = calculate_reliability_score(
      avail,
      lat_p95,
      err_rate,
      eval_res["status"],
      burn["status"],
      svc["active_incidents_count"],
  )

  return ServiceReliabilityItem(
      service=svc["name"],
      reliability_score=rel["score"],
      rating=rel["rating"],
      availability=avail,
      latency_p95_ms=lat_p95,
      error_rate=err_rate,
      throughput_rps=svc["request_rate"],
      slo_status=eval_res["status"],
      error_budget_remaining_pct=eb["remaining_pct"],
      burn_rate_status=burn["status"],
      active_incidents_count=svc["active_incidents_count"],
      trend="DEGRADED" if eval_res["status"] == "BREACHED" else "STABLE",
  )


# ---------------------------------------------------------------------------
# GET /sre/slis
# ---------------------------------------------------------------------------


@router.get(
    "/slis",
    response_model=SliMetricsItem,
    summary="Get calculated Service Level Indicators for platform or specific service",
)
async def get_slis(
    service: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SliMetricsItem:
  services = await _get_services_data(db)
  if service:
    target_svc = next(
        (s for s in services if s["name"].lower() == service.lower()), None
    )
    if target_svc:
      err_rate = target_svc["error_rate"]
      total_req = int(target_svc["request_rate"] * 3600)
      failed_req = int(total_req * (err_rate / 100.0))
      return SliMetricsItem(
          **calculate_sli_metrics(
              total_req,
              failed_req,
              [
                  target_svc["latency_p99_ms"] * 0.4,
                  target_svc["latency_p99_ms"] * 0.75,
                  target_svc["latency_p99_ms"],
              ],
          )
      )

  # Platform aggregate SLI
  tot_req = sum(int(s["request_rate"] * 3600) for s in services)
  tot_failed = sum(
      int(s["request_rate"] * 3600 * (s["error_rate"] / 100.0))
      for s in services
  )
  return SliMetricsItem(
      **calculate_sli_metrics(
          tot_req, tot_failed, [25.0, 65.0, 120.0, 240.0, 480.0]
      )
  )


# ---------------------------------------------------------------------------
# GET /sre/slos, POST /sre/slos, PUT /sre/slos/{id}
# ---------------------------------------------------------------------------


@router.get(
    "/slos",
    response_model=SloListResponse,
    summary="List configured Service Level Objectives (SLOs)",
)
async def get_slos(
    service: str | None = None,
    indicator_type: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SloListResponse:
  slos_db = await crud_sre.get_slos(
      db,
      service=service,
      indicator_type=indicator_type,
      user_id=current_user.id,
  )
  services = await _get_services_data(db)

  items = []
  for slo in slos_db:
    svc_data = next(
        (s for s in services if s["name"].lower() == slo.service.lower()), None
    )
    if slo.indicator_type == "latency":
      current_val = svc_data["latency_p99_ms"] * 0.75 if svc_data else 45.0
    elif slo.indicator_type == "error_rate":
      current_val = svc_data["error_rate"] if svc_data else 0.1
    else:
      current_val = (
          max(0.0, 100.0 - svc_data["error_rate"]) if svc_data else 99.9
      )

    eval_res = evaluate_slo(
        slo.indicator_type, slo.target, current_val, slo.target_threshold_ms
    )

    items.append(
        SloItem(
            id=slo.id,
            service=slo.service,
            name=slo.name,
            description=slo.description,
            indicator_type=slo.indicator_type,
            target=slo.target,
            target_threshold_ms=slo.target_threshold_ms,
            window=slo.window,
            enabled=slo.enabled,
            current_sli=eval_res["current_sli"],
            compliance_percentage=eval_res["compliance_percentage"],
            status=eval_res["status"],
            created_at=slo.created_at,
            updated_at=slo.updated_at,
        )
    )

  return SloListResponse(slos=items, total=len(items))


@router.post(
    "/slos",
    response_model=SloItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Service Level Objective (SLO)",
)
async def create_slo(
    payload: SloCreatePayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SloItem:
  slo = await crud_sre.create_slo(
      db, user_id=current_user.id, data=payload.model_dump()
  )
  eval_res = evaluate_slo(slo.indicator_type, slo.target, 99.9)

  return SloItem(
      id=slo.id,
      service=slo.service,
      name=slo.name,
      description=slo.description,
      indicator_type=slo.indicator_type,
      target=slo.target,
      target_threshold_ms=slo.target_threshold_ms,
      window=slo.window,
      enabled=slo.enabled,
      current_sli=eval_res["current_sli"],
      compliance_percentage=eval_res["compliance_percentage"],
      status=eval_res["status"],
      created_at=slo.created_at,
      updated_at=slo.updated_at,
  )


@router.put(
    "/slos/{slo_id}",
    response_model=SloItem,
    summary="Update an existing Service Level Objective (SLO)",
)
async def update_slo(
    slo_id: uuid.UUID,
    payload: SloUpdatePayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SloItem:
  updated = await crud_sre.update_slo(
      db, slo_id=slo_id, data=payload.model_dump(exclude_unset=True)
  )
  if not updated:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Service Level Objective not found.",
    )

  eval_res = evaluate_slo(updated.indicator_type, updated.target, 99.9)
  return SloItem(
      id=updated.id,
      service=updated.service,
      name=updated.name,
      description=updated.description,
      indicator_type=updated.indicator_type,
      target=updated.target,
      target_threshold_ms=updated.target_threshold_ms,
      window=updated.window,
      enabled=updated.enabled,
      current_sli=eval_res["current_sli"],
      compliance_percentage=eval_res["compliance_percentage"],
      status=eval_res["status"],
      created_at=updated.created_at,
      updated_at=updated.updated_at,
  )


# ---------------------------------------------------------------------------
# GET /sre/error-budgets & GET /sre/burn-rates
# ---------------------------------------------------------------------------


@router.get(
    "/error-budgets",
    response_model=list[ErrorBudgetItem],
    summary="List Error Budget consumption metrics for monitored services",
)
async def get_error_budgets(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[ErrorBudgetItem]:
  services = await _get_services_data(db)
  slos_db = await crud_sre.get_slos(db, user_id=current_user.id)

  items = []
  for s in services:
    name = s["name"]
    avail = max(0.0, 100.0 - s["error_rate"])
    matching_slo = next(
        (slo for slo in slos_db if slo.service == name), None
    )
    target_slo = matching_slo.target if matching_slo else 99.9

    eb = calculate_error_budget(target_slo, avail)
    items.append(
        ErrorBudgetItem(
            service=name,
            target_slo=target_slo,
            total_budget_pct=eb["total_budget_pct"],
            consumed_pct=eb["consumed_pct"],
            remaining_pct=eb["remaining_pct"],
            remaining_budget_units=eb["remaining_budget_units"],
            status=(
                "EXHAUSTED"
                if eb["remaining_pct"] <= 0
                else ("AT_RISK" if eb["remaining_pct"] <= 30 else "HEALTHY")
            ),
        )
    )

  return items


@router.get(
    "/burn-rates",
    response_model=list[BurnRateItem],
    summary="Get multi-window burn rate calculations (1h, 6h, 24h, 7d)",
)
async def get_burn_rates(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[BurnRateItem]:
  services = await _get_services_data(db)
  slos_db = await crud_sre.get_slos(db, user_id=current_user.id)

  items = []
  for s in services:
    name = s["name"]
    err_rate = s["error_rate"]
    avail = max(0.0, 100.0 - err_rate)
    matching_slo = next(
        (slo for slo in slos_db if slo.service == name), None
    )
    target_slo = matching_slo.target if matching_slo else 99.9

    eb = calculate_error_budget(target_slo, avail)
    burn = calculate_burn_rates(eb, err_rate)
    items.append(
        BurnRateItem(
            service=name,
            burn_1h=burn["burn_1h"],
            burn_6h=burn["burn_6h"],
            burn_24h=burn["burn_24h"],
            burn_7d=burn["burn_7d"],
            status=burn["status"],
        )
    )

  return items


# ---------------------------------------------------------------------------
# GET /sre/risks, /sre/incidents, /sre/dependencies, /sre/forecast, /sre/recommendations
# ---------------------------------------------------------------------------


@router.get(
    "/risks",
    response_model=ReliabilityRiskListResponse,
    summary="Detect active reliability risks across platform services",
)
async def get_reliability_risks(
    severity_filter: str | None = Query(default=None, alias="severity"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ReliabilityRiskListResponse:
  services = await _get_services_data(db)
  slos_db = await crud_sre.get_slos(db, user_id=current_user.id)

  all_risks = []
  for s in services:
    name = s["name"]
    err_rate = s["error_rate"]
    avail = max(0.0, 100.0 - err_rate)
    lat_p95 = round(s["latency_p99_ms"] * 0.75, 1)

    matching_slo = next(
        (slo for slo in slos_db if slo.service == name), None
    )
    target_slo = matching_slo.target if matching_slo else 99.9

    eval_res = evaluate_slo("availability", target_slo, avail)
    eb = calculate_error_budget(target_slo, avail)
    burn = calculate_burn_rates(eb, err_rate)

    risks = detect_reliability_risks(
        name,
        avail,
        lat_p95,
        err_rate,
        eval_res["status"],
        eb["remaining_pct"],
        burn["status"],
        s["active_incidents_count"],
    )
    all_risks.extend([ReliabilityRiskItem(**r) for r in risks])

  if severity_filter:
    all_risks = [
        r for r in all_risks if r.severity.upper() == severity_filter.upper()
    ]

  crit_cnt = sum(1 for r in all_risks if r.severity == "CRITICAL")
  return ReliabilityRiskListResponse(
      risks=all_risks, total_risks=len(all_risks), critical_risks=crit_cnt
  )


@router.get(
    "/incidents",
    response_model=IncidentImpactListResponse,
    summary="List correlated incidents impacting service reliability and error budgets",
)
async def get_incident_impact(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> IncidentImpactListResponse:
  inc_stmt = (
      select(Incident)
      .where(
          Incident.status.in_(
              ["OPEN", "INVESTIGATING", "MITIGATING", "DETECTED", "RESOLVED"]
          )
      )
      .order_by(Incident.created_at.desc())
      .limit(20)
  )
  inc_res = await db.execute(inc_stmt)
  incidents_db = list(inc_res.scalars().all())

  items = []
  for inc in incidents_db:
    start_t = inc.started_at or inc.created_at
    if start_t:
      if start_t.tzinfo is None:
        start_t = start_t.replace(tzinfo=UTC)
      dur = round(max(0.0, (datetime.now(UTC) - start_t).total_seconds() / 60.0), 1)
    else:
      dur = 15.0
    items.append(
        IncidentImpactItem(
            id=inc.id,
            title=inc.title,
            service=inc.affected_service or "api-gateway",
            severity=inc.severity,
            status=inc.status,
            started_at=start_t,
            duration_minutes=dur,
            slo_impact=(
                "HIGH (Target Breached)"
                if inc.severity in ("CRITICAL", "HIGH")
                else "MODERATE"
            ),
            budget_impact_pct=25.0
            if inc.severity == "CRITICAL"
            else (12.5 if inc.severity == "HIGH" else 4.0),
        )
    )

  return IncidentImpactListResponse(incidents=items, total=len(items))


@router.get(
    "/dependencies",
    response_model=DependencyImpactListResponse,
    summary="Get service dependency reliability impact and blast radius risk",
)
async def get_dependency_impact(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> DependencyImpactListResponse:
  dep_stmt = select(ServiceDependency).limit(25)
  res = await db.execute(dep_stmt)
  deps_db = list(res.scalars().all())

  items = []
  if deps_db:
    for d in deps_db:
      items.append(
          DependencyImpactItem(
              dependency=d.source_service,
              target_service=d.target_service,
              health="DEGRADED" if d.error_rate > 1.0 else "HEALTHY",
              latency_ms=round(d.latency_ms * 0.7, 1),
              error_rate=round(d.error_rate, 2),
              affected_services=[d.target_service],
              reliability_risk=(
                  "Cascading Latency Bottleneck"
                  if d.latency_ms > 200
                  else "Normal"
              ),
          )
      )
  else:
    # Fixture default dependency impact items
    items = [
        DependencyImpactItem(
            dependency="api-gateway",
            target_service="auth-service",
            health="HEALTHY",
            latency_ms=24.5,
            error_rate=0.05,
            affected_services=["auth-service", "user-service"],
            reliability_risk="Normal",
        ),
        DependencyImpactItem(
            dependency="api-gateway",
            target_service="payment-service",
            health="DEGRADED",
            latency_ms=380.0,
            error_rate=0.85,
            affected_services=["order-service", "payment-service"],
            reliability_risk="High Latency Bottleneck",
        ),
        DependencyImpactItem(
            dependency="payment-service",
            target_service="postgres-primary",
            health="DEGRADED",
            latency_ms=140.0,
            error_rate=0.45,
            affected_services=["payment-service"],
            reliability_risk="Database Lock Contention Risk",
        ),
    ]

  return DependencyImpactListResponse(dependencies=items, total=len(items))


@router.get(
    "/forecast",
    response_model=ReliabilityForecastResponse,
    summary="Predictive 24h, 7d, and 30d reliability trend forecast",
)
async def get_reliability_forecast(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ReliabilityForecastResponse:
  services = await _get_services_data(db)
  history_points = [
      {
          "availability": max(0.0, 100.0 - s["error_rate"]),
          "error_rate": s["error_rate"],
          "latency_p95_ms": s["latency_p99_ms"] * 0.75,
      }
      for s in services
  ]
  fc = forecast_reliability_trends(history_points)
  return ReliabilityForecastResponse(**fc)


@router.get(
    "/recommendations",
    response_model=SreRecommendationListResponse,
    summary="Get actionable SRE recommendations derived from live telemetry",
)
async def get_sre_recommendations(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SreRecommendationListResponse:
  services = await _get_services_data(db)
  slos_db = await crud_sre.get_slos(db, user_id=current_user.id)

  all_recs = []
  for s in services:
    name = s["name"]
    err_rate = s["error_rate"]
    avail = max(0.0, 100.0 - err_rate)
    lat_p95 = round(s["latency_p99_ms"] * 0.75, 1)

    matching_slo = next(
        (slo for slo in slos_db if slo.service == name), None
    )
    target_slo = matching_slo.target if matching_slo else 99.9

    eval_res = evaluate_slo("availability", target_slo, avail)
    eb = calculate_error_budget(target_slo, avail)
    burn = calculate_burn_rates(eb, err_rate)

    recs = generate_sre_recommendations(
        name, avail, lat_p95, err_rate, eval_res["status"], burn["status"]
    )
    all_recs.extend([SreRecommendationItem(**r) for r in recs])

  return SreRecommendationListResponse(
      recommendations=all_recs, total=len(all_recs)
  )


# ---------------------------------------------------------------------------
# POST /sre/analyze
# ---------------------------------------------------------------------------


@router.post(
    "/analyze",
    response_model=SreAnalyzeResponse,
    summary="Trigger Gemini AI / Local SRE Intelligence reliability analysis",
)
async def analyze_sre_reliability(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> SreAnalyzeResponse:
  log.info("trigger_sre_analysis", user_id=str(current_user.id))

  overview = await get_sre_overview(current_user, db)
  services = await _get_services_data(db)

  analysis = await analyze_reliability_with_gemini(
      db,
      user_id=str(current_user.id),
      sre_overview=overview.model_dump(),
      services_summary=services,
  )

  recs_out = []
  for r in analysis.get("sre_recommendations", []):
    if isinstance(r, dict):
      if "id" not in r or not r["id"]:
        r["id"] = str(uuid.uuid4())
      recs_out.append(SreRecommendationItem(**r))
    elif hasattr(r, "id"):
      recs_out.append(SreRecommendationItem.model_validate(r))

  return SreAnalyzeResponse(
      executive_summary=analysis.get("executive_summary", ""),
      critical_services=analysis.get("critical_services", []),
      error_budget_warnings=analysis.get("error_budget_warnings", []),
      sre_recommendations=recs_out,
      analyzed_at=analysis.get("analyzed_at", ""),
      analysis_engine=analysis.get("analysis_engine", "Local SRE Intelligence"),
  )
