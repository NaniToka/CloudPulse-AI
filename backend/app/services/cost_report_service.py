"""
FinOps Report Aggregator Service — compiles 12-section executive reports & exports.
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_cost
from app.services.cost_engine import (
    analyze_cost_drivers,
    calculate_budget_crossing_projection,
    calculate_cost_forecast,
    calculate_finops_health_score,
    calculate_period_comparison,
    calculate_savings_center_breakdown,
    detect_cost_anomalies,
    evaluate_budget,
    generate_executive_cost_summary,
    group_costs_by_provider,
)
from app.services.pdf_report_service import generate_finops_report_pdf


async def generate_finops_executive_report_data(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: str | None = None,
    date_range: str | None = "30_days",
) -> dict[str, Any]:
    """Compiles complete 12-section FinOps executive intelligence report data."""
    overview = await crud_cost.get_cost_overview_data(db, user_id=user_id, provider=provider, date_range=date_range)
    costs, _ = await crud_cost.get_costs(db, user_id=user_id, provider=provider, limit=500)
    recs_items, _ = await crud_cost.get_recommendations(db, user_id=user_id, status="active")
    budgets_db = await crud_cost.get_budgets(db, user_id=user_id)

    resources_dicts = [
        {
            "resource_name": c.resource_name,
            "service": c.service,
            "provider": c.provider,
            "region": c.region,
            "cost": c.cost,
            "status": c.status,
            "environment": c.environment,
        }
        for c in costs
    ]
    from app.schemas.cost import RecommendationItem

    recs_dicts = [RecommendationItem.model_validate(r, from_attributes=True).model_dump(mode="json") for r in recs_items]

    anomalies = detect_cost_anomalies(resources_dicts)
    crit_anomalies_count = sum(1 for a in anomalies if a.get("severity") == "CRITICAL")
    forecast = calculate_cost_forecast(overview["daily_trend"], overview["monthly_cost"])

    # Budget summary & crossing
    total_budget_amount = sum(b.amount for b in budgets_db) if budgets_db else 0.0
    budget_ev = evaluate_budget(total_budget_amount, overview["monthly_cost"], overview["projected_cost"])
    crossing_proj = calculate_budget_crossing_projection(total_budget_amount, overview["monthly_cost"], overview["daily_trend"])

    # Health Score & Cost Drivers & Summaries
    health_score = calculate_finops_health_score(
        monthly_cost=overview["monthly_cost"],
        potential_savings=overview["potential_savings"],
        anomalies_count=len(anomalies),
        critical_anomalies_count=crit_anomalies_count,
        budget_utilization_pct=budget_ev["utilization_pct"],
        projected_variance_pct=abs(overview["percentage_change"]),
    )
    exec_summary = generate_executive_cost_summary(
        monthly_cost=overview["monthly_cost"],
        previous_month_cost=overview["previous_month_cost"],
        percentage_change=overview["percentage_change"],
        service_breakdown=overview["service_breakdown"],
        recommendations=recs_dicts,
        anomalies=anomalies,
    )
    drivers = analyze_cost_drivers(resources_dicts, anomalies, recs_dicts)
    comparison = calculate_period_comparison(resources_dicts, overview["previous_month_cost"])
    provider_breakdown = group_costs_by_provider(resources_dicts)
    savings_center = calculate_savings_center_breakdown(recs_dicts)

    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "date_range": date_range or "30_days",
        "data_source": "Demo Data — Local Development",
        "health_score": health_score,
        "executive_summary": " ".join(exec_summary["summary_statements"]),
        "summary_statements": exec_summary["summary_statements"],
        "total_monthly_cost": overview["monthly_cost"],
        "previous_month_cost": overview["previous_month_cost"],
        "percentage_change": overview["percentage_change"],
        "projected_cost": overview["projected_cost"],
        "potential_monthly_savings": overview["potential_savings"],
        "potential_annual_savings": round(overview["potential_savings"] * 12.0, 2),
        "cost_drivers": drivers,
        "period_comparison": comparison,
        "provider_breakdown": provider_breakdown,
        "service_breakdown": overview["service_breakdown"],
        "region_breakdown": overview["region_breakdown"],
        "anomalies": anomalies,
        "forecast": forecast,
        "budget_status": budget_ev,
        "budget_crossing_projection": crossing_proj,
        "savings_center": savings_center,
        "recommendations": recs_dicts,
    }


async def generate_finops_pdf_report(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: str | None = None,
    date_range: str | None = "30_days",
) -> bytes:
    """Generates PDF binary for FinOps Executive Intelligence Report."""
    data = await generate_finops_executive_report_data(db, user_id=user_id, provider=provider, date_range=date_range)
    return generate_finops_report_pdf(data)


async def export_finops_csv(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: str | None = None,
) -> str:
    """Generates CSV format export of cloud cost inventory records."""
    costs, _ = await crud_cost.get_costs(db, user_id=user_id, provider=provider, limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Resource Name", "Service", "Provider", "Region", "Environment", "Status", "Monthly Cost ($)", "Daily Cost ($)", "Usage Amount", "Usage Unit", "Timestamp"
    ])

    for c in costs:
        writer.writerow([
            str(c.id), c.resource_name, c.service, c.provider, c.region, c.environment, c.status, f"{c.cost:.2f}", f"{c.daily_cost:.2f}", f"{c.usage_amount:.2f}", c.usage_unit, c.timestamp.isoformat()
        ])

    return output.getvalue()
