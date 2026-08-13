"""
CRUD operations for CloudCost and OptimizationRecommendation models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cloud_cost import CloudCost, CostBudget, OptimizationRecommendation
from app.schemas.cost import ServiceCostItem, ServiceCostsResponse
from app.services.cost_engine import group_costs_by_service

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
        # AWS Resources
        (
            "aws-prod-ec2-m5.2xlarge",
            "AWS EC2",
            "aws",
            "us-east-1",
            4850.00,
            161.66,
            720.0,
            "hrs",
            "production",
            "active",
        ),
        (
            "aws-rds-postgresql-primary",
            "AWS RDS",
            "aws",
            "us-east-1",
            3450.00,
            115.00,
            720.0,
            "hrs",
            "production",
            "active",
        ),
        (
            "aws-s3-logs-and-backups",
            "AWS S3",
            "aws",
            "us-west-2",
            1280.00,
            42.66,
            50.0,
            "TB",
            "production",
            "active",
        ),
        (
            "aws-cloudwatch-log-retention",
            "AWS CloudWatch",
            "aws",
            "us-east-1",
            950.00,
            31.66,
            85.0,
            "GB/day",
            "production",
            "idle",
        ),
        # Azure Resources
        (
            "azure-vm-standard-d8s-v3",
            "Azure Virtual Machines",
            "azure",
            "eastus",
            3100.00,
            103.33,
            720.0,
            "hrs",
            "production",
            "active",
        ),
        (
            "azure-blob-storage-primary",
            "Azure Storage",
            "azure",
            "eastus",
            1450.00,
            48.33,
            40.0,
            "TB",
            "production",
            "active",
        ),
        (
            "azure-sql-database-prod",
            "Azure SQL Database",
            "azure",
            "westeurope",
            2600.00,
            86.66,
            720.0,
            "hrs",
            "production",
            "active",
        ),
        # Kubernetes Resources
        (
            "k8s-compute-node-pool-cpu",
            "Kubernetes Compute",
            "kubernetes",
            "us-central1",
            5400.00,
            180.00,
            720.0,
            "core-hrs",
            "production",
            "active",
        ),
        (
            "k8s-persistent-volume-claims",
            "Kubernetes Storage",
            "kubernetes",
            "us-central1",
            1800.00,
            60.00,
            120.0,
            "GB",
            "production",
            "active",
        ),
        (
            "k8s-ingress-and-lb-networking",
            "Kubernetes Networking",
            "kubernetes",
            "us-central1",
            950.00,
            31.66,
            350.0,
            "GB-ingress",
            "production",
            "active",
        ),
        # GKE & GCP Resources
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

    await db.commit()



# ── Cost Queries ──────────────────────────────────────────────────────────────


async def get_costs(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    service: str | None = None,
    provider: str | None = None,
    region: str | None = None,
    environment: str | None = None,
    search: str | None = None,
) -> tuple[list[CloudCost], int]:
    """Fetch paginated cloud costs for a user with optional filters."""
    await seed_default_costs_if_empty(db, user_id)

    stmt = select(CloudCost).where(CloudCost.user_id == user_id)
    if service:
        stmt = stmt.where(CloudCost.service == service)
    if provider:
        stmt = stmt.where(CloudCost.provider == provider)
    if region:
        stmt = stmt.where(CloudCost.region == region)
    if environment:
        stmt = stmt.where(CloudCost.environment == environment)
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

    prev_month_cost = round(monthly_cost * 0.968, 2)
    pct_change = (
        round(((monthly_cost - prev_month_cost) / prev_month_cost) * 100.0, 1)
        if prev_month_cost > 0
        else 0.0
    )

    return {
        "monthly_cost": round(monthly_cost, 2),
        "previous_month_cost": prev_month_cost,
        "percentage_change": pct_change,
        "projected_cost": round(monthly_cost * 1.05, 2),
        "potential_savings": round(potential_savings, 2),
        "efficiency_score": efficiency,
        "active_resources_count": active_count,
        "idle_resources_count": idle_count,
        "daily_trend": daily_trend,
        "service_breakdown": service_breakdown,
        "region_breakdown": region_breakdown,
        "data_source": "Demo Provider",
        "environment": "Local Development",
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
        await db.flush()
    return record


# ── Budget CRUD ───────────────────────────────────────────────────────────────


async def seed_default_budgets_if_empty(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Seed sample FinOps budgets if user has no budget records."""
    count_stmt = select(func.count()).select_from(CostBudget).where(CostBudget.user_id == user_id)
    res = await db.execute(count_stmt)
    if res.scalar_one() > 0:
        return

    now = datetime.now(UTC)
    sample_budgets = [
        ("Engineering Department Monthly Budget", "all", "all", "production", 100000.0, "monthly", [50, 75, 90, 100]),
        ("AWS Infrastructure Budget", "aws", "EC2", "production", 15000.0, "monthly", [50, 75, 90, 100]),
        ("Azure Services Budget", "azure", "all", "production", 8000.0, "monthly", [50, 75, 90, 100]),
        ("Kubernetes Cluster Compute Budget", "kubernetes", "Compute", "production", 12000.0, "monthly", [50, 75, 90, 100]),
    ]

    for name, provider, service, env, amt, period, thresholds in sample_budgets:
        b = CostBudget(
            id=uuid.uuid4(),
            name=name,
            provider=provider,
            service=service,
            environment=env,
            amount=amt,
            period=period,
            threshold_percentages=thresholds,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        db.add(b)

    await db.flush()


async def get_budgets(db: AsyncSession, user_id: uuid.UUID) -> list[CostBudget]:
    """Fetch all cost budgets for user."""
    await seed_default_budgets_if_empty(db, user_id)
    stmt = select(CostBudget).where(CostBudget.user_id == user_id).order_by(CostBudget.amount.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def create_budget(db: AsyncSession, user_id: uuid.UUID, data: dict[str, Any]) -> CostBudget:
    """Create a new FinOps cost budget."""
    b = CostBudget(
        id=uuid.uuid4(),
        name=data["name"],
        provider=data.get("provider", "all"),
        service=data.get("service", "all"),
        environment=data.get("environment", "all"),
        amount=float(data["amount"]),
        period=data.get("period", "monthly"),
        threshold_percentages=data.get("threshold_percentages", [50, 75, 90, 100]),
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(b)
    await db.flush()
    return b


async def update_budget(
    db: AsyncSession, user_id: uuid.UUID, budget_id: uuid.UUID, data: dict[str, Any]
) -> CostBudget | None:
    """Update an existing FinOps cost budget."""
    stmt = select(CostBudget).where(CostBudget.id == budget_id, CostBudget.user_id == user_id)
    res = await db.execute(stmt)
    b = res.scalar_one_or_none()
    if not b:
        return None
    if "name" in data and data["name"]:
        b.name = data["name"]
    if "amount" in data and data["amount"] is not None:
        b.amount = float(data["amount"])
    if "period" in data and data["period"]:
        b.period = data["period"]
    if "threshold_percentages" in data and data["threshold_percentages"]:
        b.threshold_percentages = data["threshold_percentages"]
    if "provider" in data and data["provider"]:
        b.provider = data["provider"]
    if "service" in data and data["service"]:
        b.service = data["service"]

    b.updated_at = datetime.now(UTC)
    db.add(b)
    await db.flush()
    return b


async def calculate_budget_spend(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: str = "all",
    service: str = "all",
    environment: str = "all",
) -> float:
    """Calculate actual monthly cost filtered by provider, service, and environment."""
    stmt = select(CloudCost).where(CloudCost.user_id == user_id)
    if provider and provider.lower() != "all":
        stmt = stmt.where(func.lower(CloudCost.provider) == provider.lower())
    if service and service.lower() != "all":
        stmt = stmt.where(func.lower(CloudCost.service) == service.lower())
    if environment and environment.lower() != "all":
        stmt = stmt.where(func.lower(CloudCost.environment) == environment.lower())

    res = await db.execute(stmt)
    matching_costs = list(res.scalars().all())
    return round(sum(c.cost for c in matching_costs), 2)


async def get_filtered_costs(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    service: str | None = None,
    provider: str | None = None,
    region: str | None = None,
    environment: str | None = None,
    search: str | None = None,
    sort_by: str = "cost",
    sort_dir: str = "desc",
    page: int = 1,
    size: int = 20,
) -> tuple[list[CloudCost], int, float]:
    """Fetch paginated & filtered cloud costs with total cost sum."""
    skip = max(0, (page - 1) * size)
    items, total = await get_costs(
        db,
        user_id=user_id,
        skip=skip,
        limit=size,
        service=service,
        provider=provider,
        region=region,
        environment=environment,
        search=search,
    )
    total_cost = round(sum(c.cost for c in items), 2)
    return items, total, total_cost


async def get_service_costs_data(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
) -> ServiceCostsResponse:
    """Fetch service-level breakdown response object."""
    costs, _ = await get_costs(db, user_id=user_id, limit=300)
    resources_dicts = [{"cost": c.cost, "service": c.service} for c in costs]
    services = [ServiceCostItem(**s) for s in group_costs_by_service(resources_dicts)]
    total = sum(s.cost for s in services)
    return ServiceCostsResponse(
        services=services,
        total_cost=round(total, 2),
    )

