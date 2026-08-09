"""
Pydantic schemas for the Cloud Cost Optimizer module.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# ── Shared Sub-Schemas ────────────────────────────────────────────────────────


class DailyCostItem(BaseModel):
    date: str
    cost: float


class ServiceCostItem(BaseModel):
    service: str
    cost: float
    percentage: float
    resource_count: int
    fill: str | None = None


class RegionCostItem(BaseModel):
    region: str
    cost: float
    percentage: float
    resource_count: int


# ── Cloud Cost Resource Item ──────────────────────────────────────────────────


class CloudCostItem(BaseModel):
    id: uuid.UUID
    resource_name: str
    service: str
    provider: str
    region: str
    cost: float
    daily_cost: float
    usage_amount: float
    usage_unit: str
    environment: str
    status: str
    tags: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime

    model_config = {"from_attributes": True}


class CloudCostListResponse(BaseModel):
    items: list[CloudCostItem]
    total: int


# ── Optimization Recommendation Item ─────────────────────────────────────────


class RecommendationItem(BaseModel):
    id: uuid.UUID
    resource_id: uuid.UUID | None = None
    resource_name: str
    service: str
    recommendation_type: (
        str  # idle_resource | wasted_resource | rightsizing | reserved_instance | auto_scaling
    )
    title: str
    description: str
    current_cost: float
    estimated_savings: float
    effort_level: str  # low | medium | high
    risk_level: str  # low | medium | high
    status: str  # active | dismissed | applied
    ai_summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationsResponse(BaseModel):
    items: list[RecommendationItem]
    total: int
    total_savings: float


# ── Cost Overview Response ────────────────────────────────────────────────────


class CostOverviewResponse(BaseModel):
    monthly_cost: float
    previous_month_cost: float
    percentage_change: float
    projected_cost: float
    potential_savings: float
    efficiency_score: int
    active_resources_count: int
    idle_resources_count: int
    daily_trend: list[DailyCostItem]
    service_breakdown: list[ServiceCostItem]
    region_breakdown: list[RegionCostItem]
    data_source: str = Field(default="Demo Provider", description="Data source provider")
    environment: str = Field(default="Local Development", description="Execution environment")



# ── Service-wise Costs Response ───────────────────────────────────────────────


class ServiceCostsResponse(BaseModel):
    services: list[ServiceCostItem]
    total_cost: float


# ── AI Cost Analysis Response ─────────────────────────────────────────────────


class CostAnalyzeResponse(BaseModel):
    cost_summary: str
    highest_cost_services: list[str]
    idle_resources: list[str]
    wasted_resources: list[str]
    optimization_suggestions: list[str]
    reserved_instance_recommendations: list[str]
    auto_scaling_recommendations: list[str]
    estimated_monthly_savings: float
    recommendations: list[RecommendationItem]
    efficiency_score: int
    analyzed_at: datetime
