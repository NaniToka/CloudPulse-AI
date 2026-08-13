"""
Executive Cloud Operations Command Center API Endpoints.
"""

from __future__ import annotations

import csv
import io
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.models.user import User
from app.schemas.executive import (
    CloudProviderHealthResponse,
    CloudRiskMatrixResponse,
    ExecutiveAlertsResponse,
    ExecutiveOverviewResponse,
    ExecutivePriorityItem,
    ExecutivePriorityListResponse,
    ExecutiveRecommendationsResponse,
    ExecutiveSummaryResponse,
    HealthScoreResponse,
    KeyExecutiveMetricsResponse,
    OperationalTrendsResponse,
    ProviderHealthItem,
    RiskMatrixItem,
    ServiceHealthMapResponse,
    WhatChangedResponse,
)
from app.services import executive_engine, pdf_report_service

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /executive/overview
# ---------------------------------------------------------------------------


@router.get(
    "/overview",
    response_model=ExecutiveOverviewResponse,
    summary="Get full Executive Command Center aggregated overview payload",
)
async def get_executive_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveOverviewResponse:
    health = await executive_engine.calculate_cloud_operations_health_score(db, user_id=current_user.id)
    summary = await executive_engine.generate_executive_summary(db, user_id=current_user.id)
    metrics = await executive_engine.calculate_key_executive_metrics(db, user_id=current_user.id)
    priorities = await executive_engine.calculate_top_priorities(db, user_id=current_user.id)
    providers = await executive_engine.aggregate_cloud_provider_health(db, user_id=current_user.id)
    trends = await executive_engine.calculate_operational_trends(db, user_id=current_user.id)
    risks = await executive_engine.calculate_cloud_risk_matrix(db, user_id=current_user.id)
    changes = await executive_engine.aggregate_what_changed(db, user_id=current_user.id)
    alerts = await executive_engine.generate_executive_alerts(db, user_id=current_user.id)

    return ExecutiveOverviewResponse(
        health_score=HealthScoreResponse(**health),
        summary=ExecutiveSummaryResponse(**summary),
        metrics=KeyExecutiveMetricsResponse(**metrics),
        top_priorities=[ExecutivePriorityItem(**p) for p in priorities],
        provider_health=[ProviderHealthItem(**p) for p in providers],
        operational_trends=trends,
        risk_matrix=[RiskMatrixItem(**r) for r in risks],
        what_changed=changes,
        alerts=alerts,
        mode_indicator="DEMO / LOCAL MODE — Executive Intelligence Operating on Real Aggregated Platform Data",
    )


# ---------------------------------------------------------------------------
# GET /executive/health & /summary
# ---------------------------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthScoreResponse,
    summary="Get detailed Cloud Operations Health Score and component breakdowns",
)
async def get_health_score(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> HealthScoreResponse:
    health = await executive_engine.calculate_cloud_operations_health_score(db, user_id=current_user.id)
    return HealthScoreResponse(**health)


@router.get(
    "/summary",
    response_model=ExecutiveSummaryResponse,
    summary="Get AI-powered or Local Operations Executive Summary",
)
async def get_executive_summary(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveSummaryResponse:
    summary = await executive_engine.generate_executive_summary(db, user_id=current_user.id)
    return ExecutiveSummaryResponse(**summary)


# ---------------------------------------------------------------------------
# GET /executive/priorities & /trends
# ---------------------------------------------------------------------------


@router.get(
    "/priorities",
    response_model=ExecutivePriorityListResponse,
    summary="Get top prioritized executive action queue",
)
async def get_top_priorities(
    domain: str | None = None,
    severity: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutivePriorityListResponse:
    priorities = await executive_engine.calculate_top_priorities(db, user_id=current_user.id)

    if domain:
        priorities = [p for p in priorities if p["domain"].lower() == domain.lower()]
    if severity:
        priorities = [p for p in priorities if p["severity"].lower() == severity.lower()]

    p0 = sum(1 for p in priorities if p["priority_level"] == "P0")
    p1 = sum(1 for p in priorities if p["priority_level"] == "P1")

    return ExecutivePriorityListResponse(
        priorities=[ExecutivePriorityItem(**p) for p in priorities],
        total=len(priorities),
        p0_count=p0,
        p1_count=p1,
    )


@router.get(
    "/trends",
    response_model=OperationalTrendsResponse,
    summary="Get period-over-period operational trends analysis",
)
async def get_operational_trends(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTrendsResponse:
    trends = await executive_engine.calculate_operational_trends(db, user_id=current_user.id)
    return OperationalTrendsResponse(trends=trends)


# ---------------------------------------------------------------------------
# GET /executive/providers & /services & /risks & /changes & /timeline
# ---------------------------------------------------------------------------


@router.get(
    "/providers",
    response_model=CloudProviderHealthResponse,
    summary="Get cloud provider health and posture breakdown (AWS, Azure, GCP, K8s)",
)
async def get_provider_health(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CloudProviderHealthResponse:
    providers = await executive_engine.aggregate_cloud_provider_health(db, user_id=current_user.id)
    return CloudProviderHealthResponse(providers=[ProviderHealthItem(**p) for p in providers])


@router.get(
    "/services",
    response_model=ServiceHealthMapResponse,
    summary="Get Executive Service Health Map",
)
async def get_service_health_map(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceHealthMapResponse:
    services = await executive_engine.aggregate_service_health_map(db, user_id=current_user.id)
    healthy = sum(1 for s in services if s["status"] == "HEALTHY")
    degraded = sum(1 for s in services if s["status"] == "DEGRADED")
    critical = sum(1 for s in services if s["status"] == "CRITICAL")

    return ServiceHealthMapResponse(
        services=services,
        healthy_count=healthy,
        degraded_count=degraded,
        critical_count=critical,
    )


@router.get(
    "/risks",
    response_model=CloudRiskMatrixResponse,
    summary="Get Cloud Risk Matrix across operational domains",
)
async def get_risk_matrix(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> CloudRiskMatrixResponse:
    matrix = await executive_engine.calculate_cloud_risk_matrix(db, user_id=current_user.id)
    return CloudRiskMatrixResponse(matrix=[RiskMatrixItem(**r) for r in matrix])


@router.get(
    "/changes",
    response_model=WhatChangedResponse,
    summary="Get period-over-period What Changed comparison delta",
)
async def get_what_changed(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> WhatChangedResponse:
    changes = await executive_engine.aggregate_what_changed(db, user_id=current_user.id)
    return WhatChangedResponse(changes=changes, period_days=30)


@router.get(
    "/timeline",
    summary="Get unified operational timeline feed",
)
async def get_executive_timeline(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    events = await executive_engine.aggregate_executive_timeline(db, user_id=current_user.id)
    return {"events": events, "total": len(events)}


@router.get(
    "/alerts",
    response_model=ExecutiveAlertsResponse,
    summary="Get executive alert cards",
)
async def get_executive_alerts(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveAlertsResponse:
    alerts = await executive_engine.generate_executive_alerts(db, user_id=current_user.id)
    return ExecutiveAlertsResponse(alerts=alerts)


@router.get(
    "/recommendations",
    response_model=ExecutiveRecommendationsResponse,
    summary="Get executive engineering recommendations",
)
async def get_executive_recommendations(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutiveRecommendationsResponse:
    recs = await executive_engine.generate_executive_recommendations(db, user_id=current_user.id)
    return ExecutiveRecommendationsResponse(recommendations=recs)


# ---------------------------------------------------------------------------
# POST /executive/export/pdf & /csv
# ---------------------------------------------------------------------------


@router.post(
    "/export/pdf",
    summary="Export Executive Cloud Operations Report as PDF",
)
async def export_executive_pdf(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    health = await executive_engine.calculate_cloud_operations_health_score(db, user_id=current_user.id)
    summary = await executive_engine.generate_executive_summary(db, user_id=current_user.id)
    priorities = await executive_engine.calculate_top_priorities(db, user_id=current_user.id)
    metrics = await executive_engine.calculate_key_executive_metrics(db, user_id=current_user.id)

    title = "CloudPulse-AI — Executive Operations Intelligence Report"
    content = (
        f"EXECUTIVE SUMMARY:\n{summary['summary_text']}\n\n"
        f"HEALTH SCORE: {health['overall_score']}/100 ({health['risk_level']})\n"
        f"Reliability: {health['reliability_score']} | Security: {health['security_score']} | Cost: {health['cost_score']}\n\n"
        f"KEY METRICS:\n"
        f"- Active Incidents: {metrics['active_incidents']} (Critical: {metrics['critical_incidents']})\n"
        f"- Security Findings: {metrics['security_findings']} (Critical: {metrics['critical_security_findings']})\n"
        f"- Monthly Spend: ${metrics['current_monthly_spend']:,.2f}\n"
        f"- FinOps Potential Savings: ${metrics['potential_savings']:,.2f}\n\n"
        f"TOP PRIORITIES:\n"
    )
    for p in priorities[:3]:
        content += f"- [{p['priority_level']}] {p['title']} ({p['domain']}): {p['recommended_action']}\n"

    pdf_bytes = pdf_report_service.generate_pdf_bytes(title=title, content=content)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="Executive_Cloud_Operations_Report.pdf"'},
    )


@router.post(
    "/export/csv",
    summary="Export Executive Metrics as CSV",
)
async def export_executive_csv(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    metrics = await executive_engine.calculate_key_executive_metrics(db, user_id=current_user.id)
    health = await executive_engine.calculate_cloud_operations_health_score(db, user_id=current_user.id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric Name", "Value"])
    writer.writerow(["Cloud Operations Health Score", health["overall_score"]])
    writer.writerow(["Risk Level", health["risk_level"]])
    writer.writerow(["Active Incidents", metrics["active_incidents"]])
    writer.writerow(["Critical Incidents", metrics["critical_incidents"]])
    writer.writerow(["Security Findings", metrics["security_findings"]])
    writer.writerow(["Critical Security Findings", metrics["critical_security_findings"]])
    writer.writerow(["Monthly Spend (USD)", metrics["current_monthly_spend"]])
    writer.writerow(["Potential Savings (USD)", metrics["potential_savings"]])
    writer.writerow(["Budget Utilization (%)", metrics["budget_utilization_pct"]])
    writer.writerow(["Policy Violations", metrics["policy_violations"]])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="Executive_Cloud_Metrics.csv"'},
    )
