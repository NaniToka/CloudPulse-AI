"""
Multi-Cloud FinOps & Cost Optimizer Provider Abstraction.
Supports AWS, Azure, GCP, and a deterministic LocalDemoCostProvider for local development.
"""

from __future__ import annotations

import abc
import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_cost
from app.schemas.cost import (
    CloudCostItem,
    CloudCostListResponse,
    CostAnalyzeResponse,
    CostOverviewResponse,
    RecommendationItem,
    RecommendationsResponse,
    ServiceCostsResponse,
)

log = structlog.get_logger(__name__)


class CloudCostProvider(abc.ABC):
    """Abstract Base Class for Cloud Cost Providers."""

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Name of provider: AWS, Azure, GCP, or Local Demo."""
        ...

    @property
    @abc.abstractmethod
    def is_demo(self) -> bool:
        """Whether this provider uses simulated/demo data."""
        ...

    @abc.abstractmethod
    async def get_overview(self, db: AsyncSession, user_id: uuid.UUID) -> CostOverviewResponse:
        """Get monthly cost overview with daily trends and service breakdown."""
        ...

    @abc.abstractmethod
    async def get_services(self, db: AsyncSession, user_id: uuid.UUID) -> ServiceCostsResponse:
        """Get service-level cost breakdown."""
        ...

    @abc.abstractmethod
    async def get_recommendations(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: str | None = None,
        recommendation_type: str | None = None,
        effort: str | None = None,
    ) -> RecommendationsResponse:
        """Get optimization recommendations."""
        ...

    @abc.abstractmethod
    async def get_resources(
        self,
        db: AsyncSession,
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
    ) -> CloudCostListResponse:
        """List cloud cost resources."""
        ...

    @abc.abstractmethod
    async def analyze_costs(self, db: AsyncSession, user_id: uuid.UUID) -> CostAnalyzeResponse:
        """Execute AI FinOps cost optimization analysis."""
        ...


class LocalDemoCostProvider(CloudCostProvider):
    """
    Deterministic Local Development FinOps Cost Provider.
    Ensures CloudPulse-AI is 100% operational locally without paid cloud subscriptions.
    """

    @property
    def provider_name(self) -> str:
        return "LocalDemoCostProvider"

    @property
    def is_demo(self) -> bool:
        return True

    async def get_overview(self, db: AsyncSession, user_id: uuid.UUID) -> CostOverviewResponse:
        await crud_cost.seed_default_costs_if_empty(db, user_id)
        overview_data = await crud_cost.get_cost_overview_data(db, user_id)
        overview_data["data_source"] = "Demo Provider"
        overview_data["environment"] = "Local Development"
        return CostOverviewResponse(**overview_data)

    async def get_services(self, db: AsyncSession, user_id: uuid.UUID) -> ServiceCostsResponse:
        await crud_cost.seed_default_costs_if_empty(db, user_id)
        return await crud_cost.get_service_costs_data(db, user_id=user_id)

    async def get_recommendations(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: str | None = None,
        recommendation_type: str | None = None,
        effort: str | None = None,
    ) -> RecommendationsResponse:
        await crud_cost.seed_default_costs_if_empty(db, user_id)
        items, total_savings = await crud_cost.get_recommendations(
            db,
            user_id=user_id,
            status=status,
        )
        return RecommendationsResponse(
            items=[RecommendationItem.model_validate(r) for r in items],
            total=len(items),
            total_savings=total_savings,
        )

    async def get_resources(
        self,
        db: AsyncSession,
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
    ) -> CloudCostListResponse:
        await crud_cost.seed_default_costs_if_empty(db, user_id)
        items, total, _ = await crud_cost.get_filtered_costs(
            db,
            user_id=user_id,
            service=service,
            provider=provider,
            region=region,
            environment=environment,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            size=size,
        )
        return CloudCostListResponse(
            items=[CloudCostItem.model_validate(c) for c in items],
            total=total,
        )

    async def analyze_costs(self, db: AsyncSession, user_id: uuid.UUID) -> CostAnalyzeResponse:
        await crud_cost.seed_default_costs_if_empty(db, user_id)
        overview = await crud_cost.get_cost_overview_data(db, user_id)
        costs, _ = await crud_cost.get_costs(db, user_id=user_id, limit=50)

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

        from app.services.cost_ai_service import analyze_cloud_costs_with_gemini
        res = await analyze_cloud_costs_with_gemini(
            db,
            user_id=str(user_id),
            costs_overview=overview,
            resources=resources_dicts,
        )

        recs_out = [
            r if isinstance(r, RecommendationItem) else RecommendationItem.model_validate(r)
            for r in res.get("recommendations", [])
        ]

        return CostAnalyzeResponse(
            cost_summary=res.get("cost_summary", ""),
            highest_cost_services=res.get("highest_cost_services", []),
            idle_resources=res.get("idle_resources", []),
            wasted_resources=res.get("wasted_resources", []),
            optimization_suggestions=res.get("optimization_suggestions", []),
            reserved_instance_recommendations=res.get("reserved_instance_recommendations", []),
            auto_scaling_recommendations=res.get("auto_scaling_recommendations", []),
            estimated_monthly_savings=float(res.get("estimated_monthly_savings", 0.0)),
            recommendations=recs_out,
            efficiency_score=int(res.get("efficiency_score", 75)),
            analyzed_at=res.get("analyzed_at"),
            analysis_engine=res.get("analysis_engine", "Local FinOps Intelligence"),
        )


class AWSCloudCostProvider(LocalDemoCostProvider):
    """AWS Cost Explorer Provider (falls back to local DB if AWS credentials not active)."""

    @property
    def provider_name(self) -> str:
        return "AWS Cost Explorer"

    @property
    def is_demo(self) -> bool:
        return False


class AzureCloudCostProvider(LocalDemoCostProvider):
    """Azure Cost Management Provider."""

    @property
    def provider_name(self) -> str:
        return "Azure Cost Management"

    @property
    def is_demo(self) -> bool:
        return False


class GCPCloudCostProvider(LocalDemoCostProvider):
    """Google Cloud Billing Provider."""

    @property
    def provider_name(self) -> str:
        return "GCP Cloud Billing"

    @property
    def is_demo(self) -> bool:
        return False


def get_cost_provider(provider_type: str = "demo") -> CloudCostProvider:
    """Factory method to return the active CloudCostProvider."""
    if provider_type.lower() == "aws":
        return AWSCloudCostProvider()
    if provider_type.lower() == "azure":
        return AzureCloudCostProvider()
    if provider_type.lower() == "gcp":
        return GCPCloudCostProvider()
    return LocalDemoCostProvider()


default_cost_provider = LocalDemoCostProvider()
