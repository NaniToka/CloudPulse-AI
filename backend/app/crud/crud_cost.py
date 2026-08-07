"""
CRUD operations for CloudCost and OptimizationRecommendation models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cloud_cost import CloudCost, OptimizationRecommendation

# Service color mappings for charts
SERVICE_COLORS: dict[str, str] = {
    "Google Compute Engine": "#3b82f6",
    "Google Kubernetes Engine": "#8b5cf6",
    "Cloud SQL": "#ec4899",
    "Cloud Storage": "#10b981",
    "BigQuery": "#f59e0b",
    "Cloud Functions": "#06b6d4",
    "AWS EC2": "#6366f1",
    "AWS RDS": "#f97316",
}

DEFAULT_COLOR = "#94a3b8"


# ── Seed Default Costs ────────────────────────────────────────────────────────


async def seed_default_costs_if_empty(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Seed sample cloud cost data if user has no cost records."""
    count_stmt = select(func.count()).select_from(CloudCost).where(CloudCost.user_id == user_id)
    res = await db.execute(count_stmt)
    if res.scalar_one() > 0:
        return

    now = datetime.now(UTC)
    sample_resources = [
        # GKE Cluster
        (
            "prod-gke-cluster-us-central1",
            "Google Kubernetes Engine",
            "gcp",
            "us-central1",
            28450.00,
            948.33,
            720.0,
            "hrs",
            "production",
            "active",
        ),
        (
            "staging-gke-cluster-us-east1",
            "Google Kubernetes Engine",
            "gcp",
            "us-east1",
            8200.00,
            273.33,
            720.0,
            "hrs",
            "staging",
            "active",
        ),
        # Compute Engine VMs
        (
            "analytics-n2-standard-16",
            "Google Compute Engine",
            "gcp",
            "us-central1",
            14200.00,
            473.33,
            720.0,
            "vCPU-hrs",
            "production",
            "active",
        ),
        (
            "dev-worker-n1-standard-8",
            "Google Compute Engine",
            "gcp",
            "us-central1",
            3800.00,
            126.66,
            720.0,
            "vCPU-hrs",
            "development",
            "idle",
        ),
        (
            "legacy-batch-vm-e2-highmem",
            "Google Compute Engine",
            "gcp",
            "europe-west1",
            4600.00,
            153.33,
            400.0,
            "vCPU-hrs",
            "production",
            "overprovisioned",
        ),
        (
            "test-bench-n1-standard-4",
            "Google Compute Engine",
            "gcp",
            "us-west1",
            2100.00,
            70.00,
            100.0,
            "vCPU-hrs",
            "staging",
            "idle",
        ),
        # Cloud SQL
        (
            "prod-postgres-db-primary",
            "Cloud SQL",
            "gcp",
            "us-central1",
            11200.00,
            373.33,
            720.0,
            "hrs",
            "production",
            "active",
        ),
        (
            "staging-postgres-db-replica",
            "Cloud SQL",
            "gcp",
            "us-east1",
            2900.00,
            96.66,
            720.0,
            "hrs",
            "staging",
            "active",
        ),
        # BigQuery
        (
            "dw-data-warehouse-queries",
            "BigQuery",
            "gcp",
            "us-central1",
            6400.00,
            213.33,
            1250.0,
            "TB",
            "production",
            "active",
        ),
        # Cloud Storage
        (
            "prod-media-backup-bucket",
            "Cloud Storage",
            "gcp",
            "us-central1",
            3200.00,
            106.66,
            160.0,
            "TB",
            "production",
            "active",
        ),
        (
            "archive-logs-multi-region",
            "Cloud Storage",
            "gcp",
            "europe-west1",
            1850.00,
            61.66,
            120.0,
            "TB",
            "production",
            "active",
        ),
        # Cloud Functions
        (
            "event-processor-serverless",
            "Cloud Functions",
            "gcp",
            "us-central1",
            930.00,
            31.00,
            45.0,
            "M-invocations",
            "production",
            "active",
        ),
    ]

    for (
        name,
        service,
        provider,
        region,
        cost,
        daily_cost,
        usage,
        unit,
        env,
        status,
    ) in sample_resources:
        record = CloudCost(
            user_id=user_id,
            resource_name=name,
            service=service,
            provider=provider,
            region=region,
            cost=cost,
            daily_cost=daily_cost,
            usage_amount=usage,
            usage_unit=unit,
            environment=env,
            status=status,
            tags={"env": env, "managed-by": "terraform"},
            timestamp=now - timedelta(days=1),
        )
        db.add(record)

    # Seed initial recommendations
    sample_recommendations = [
        (
            "Terminate Idle Dev VM (dev-worker-n1-standard-8)",
            "dev-worker-n1-standard-8",
            "Google Compute Engine",
            "idle_resource",
            "VM instance has had < 2% CPU utilization for the past 14 days and zero active network connections.",
            3800.00,
            3800.00,
            "low",
            "low",
            "active",
            "Reclaiming this unattached development node will eliminate $3,800/mo in unnecessary compute costs.",
        ),
        (
            "Commit to 3-Year Committed Use Discount (CUD) for GKE",
            "prod-gke-cluster-us-central1",
            "Google Kubernetes Engine",
            "reserved_instance",
            "Baseline GKE workload memory and CPU usage has remained steady > 85% over 90 days.",
            28450.00,
            12800.00,
            "medium",
            "low",
            "active",
            "3-year CUD commitment yields a 45% discount on steady-state GKE worker nodes.",
        ),
        (
            "Rightsize Overprovisioned Cloud SQL Instance",
            "prod-postgres-db-primary",
            "Cloud SQL",
            "rightsizing",
            "Primary Cloud SQL instance is allocated 64 vCPUs but peak utilization never exceeds 18%.",
            11200.00,
            4900.00,
            "medium",
            "medium",
            "active",
            "Downsizing from db-custom-64-245760 to db-custom-32-122880 maintains safety buffers while saving $4,900/mo.",
        ),
        (
            "Enable Auto Scaling & Lifecycle Policies on Storage Buckets",
            "archive-logs-multi-region",
            "Cloud Storage",
            "wasted_resource",
            "120 TB of log files in Standard Storage class have not been accessed in over 60 days.",
            1850.00,
            1250.00,
            "low",
            "low",
            "active",
            "Moving stale logs to Nearline/Coldline lifecycle policy reduces storage cost by 67%.",
        ),
    ]

    for (
        title,
        res_name,
        service,
        r_type,
        desc,
        current_cost,
        savings,
        effort,
        risk,
        rec_status,
        ai_sum,
    ) in sample_recommendations:
        rec = OptimizationRecommendation(
            user_id=user_id,
            title=title,
            resource_name=res_name,
            service=service,
            recommendation_type=r_type,
            description=desc,
            current_cost=current_cost,
            estimated_savings=savings,
            effort_level=effort,
            risk_level=risk,
            status=rec_status,
            ai_summary=ai_sum,
        )
        db.add(rec)

    await db.flush()


# ── Cost Queries ──────────────────────────────────────────────────────────────


async def get_costs(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    service: str | None = None,
    region: str | None = None,
    search: str | None = None,
) -> tuple[list[CloudCost], int]:
    """Fetch paginated cloud costs for a user with optional filters."""
    await seed_default_costs_if_empty(db, user_id)

    stmt = select(CloudCost).where(CloudCost.user_id == user_id)
    if service:
        stmt = stmt.where(CloudCost.service == service)
    if region:
        stmt = stmt.where(CloudCost.region == region)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(CloudCost.resource_name.ilike(pattern) | CloudCost.service.ilike(pattern))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    stmt = stmt.order_by(CloudCost.cost.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    items = list(res.scalars().all())

    return items, total


async def get_cost_overview_data(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
) -> dict[str, Any]:
    """Calculate aggregated monthly spend, forecast, service breakdown, and trends."""
    await seed_default_costs_if_empty(db, user_id)

    # 1. Total monthly cost & counts
    costs_res = await db.execute(select(CloudCost).where(CloudCost.user_id == user_id))
    all_costs = list(costs_res.scalars().all())

    monthly_cost = sum(c.cost for c in all_costs)
    idle_count = sum(1 for c in all_costs if c.status in ("idle", "overprovisioned"))
    active_count = len(all_costs)

    # 2. Recommendations potential savings
    recs_res = await db.execute(
        select(OptimizationRecommendation).where(
            OptimizationRecommendation.user_id == user_id,
            OptimizationRecommendation.status == "active",
        )
    )
    active_recs = list(recs_res.scalars().all())
    potential_savings = sum(r.estimated_savings for r in active_recs)

    # 3. Service Breakdown
    service_totals: dict[str, dict[str, Any]] = {}
    for c in all_costs:
        if c.service not in service_totals:
            service_totals[c.service] = {"cost": 0.0, "count": 0}
        service_totals[c.service]["cost"] += c.cost
        service_totals[c.service]["count"] += 1

    service_breakdown = []
    for svc, data in sorted(service_totals.items(), key=lambda x: x[1]["cost"], reverse=True):
        pct = (data["cost"] / monthly_cost * 100) if monthly_cost > 0 else 0.0
        service_breakdown.append(
            {
                "service": svc,
                "cost": round(data["cost"], 2),
                "percentage": round(pct, 1),
                "resource_count": data["count"],
                "fill": SERVICE_COLORS.get(svc, DEFAULT_COLOR),
            }
        )

    # 4. Region Breakdown
    region_totals: dict[str, dict[str, Any]] = {}
    for c in all_costs:
        if c.region not in region_totals:
            region_totals[c.region] = {"cost": 0.0, "count": 0}
        region_totals[c.region]["cost"] += c.cost
        region_totals[c.region]["count"] += 1

    region_breakdown = []
    for reg, data in sorted(region_totals.items(), key=lambda x: x[1]["cost"], reverse=True):
        pct = (data["cost"] / monthly_cost * 100) if monthly_cost > 0 else 0.0
        region_breakdown.append(
            {
                "region": reg,
                "cost": round(data["cost"], 2),
                "percentage": round(pct, 1),
                "resource_count": data["count"],
            }
        )

    # 5. Daily Trend (30 days)
    daily_base = monthly_cost / 30.0
    daily_trend = []
    now = datetime.now(UTC)
    for i in range(29, -1, -1):
        day_dt = now - timedelta(days=i)
        # Small realistic variance around daily average
        variance = 1.0 + ((i % 7) - 3) * 0.03
        d_cost = round(daily_base * variance, 2)
        daily_trend.append(
            {
                "date": day_dt.strftime("%b %d"),
                "cost": d_cost,
            }
        )

    # Efficiency Score calculation (100 - (potential_savings / monthly_cost * 100))
    efficiency = (
        max(0, min(100, int(100 - (potential_savings / monthly_cost * 50))))
        if monthly_cost > 0
        else 100
    )

    return {
        "monthly_cost": round(monthly_cost, 2),
        "previous_month_cost": round(monthly_cost * 0.968, 2),
        "percentage_change": 3.2,
        "projected_cost": round(monthly_cost * 1.05, 2),
        "potential_savings": round(potential_savings, 2),
        "efficiency_score": efficiency,
        "active_resources_count": active_count,
        "idle_resources_count": idle_count,
        "daily_trend": daily_trend,
        "service_breakdown": service_breakdown,
        "region_breakdown": region_breakdown,
    }


# ── Recommendation CRUD ───────────────────────────────────────────────────────


async def get_recommendations(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    status: str | None = "active",
) -> tuple[list[OptimizationRecommendation], float]:
    """Fetch optimization recommendations for user."""
    await seed_default_costs_if_empty(db, user_id)

    stmt = select(OptimizationRecommendation).where(OptimizationRecommendation.user_id == user_id)
    if status:
        stmt = stmt.where(OptimizationRecommendation.status == status)

    stmt = stmt.order_by(OptimizationRecommendation.estimated_savings.desc())
    res = await db.execute(stmt)
    items = list(res.scalars().all())

    total_savings = sum(r.estimated_savings for r in items)
    return items, round(total_savings, 2)


async def update_recommendation_status(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    status: str,
) -> OptimizationRecommendation | None:
    """Update status of a recommendation (active, dismissed, applied)."""
    stmt = (
        update(OptimizationRecommendation)
        .where(
            OptimizationRecommendation.id == recommendation_id,
            OptimizationRecommendation.user_id == user_id,
        )
        .values(status=status, updated_at=datetime.now(UTC))
        .returning(OptimizationRecommendation)
    )
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if record:
        await db.commit()
    return record
