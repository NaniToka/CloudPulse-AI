"""
Pydantic schemas for the Cloud Cost Optimizer module.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional
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
    fill: Optional[str] = None


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
    tags: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime

    model_config = {"from_attributes": True}


class CloudCostListResponse(BaseModel):
    items: List[CloudCostItem]
    total: int


# ── Optimization Recommendation Item ─────────────────────────────────────────

class RecommendationItem(BaseModel):
    id: uuid.UUID
    resource_id: Optional[uuid.UUID] = None
    resource_name: str
    service: str
    recommendation_type: str  # idle_resource | wasted_resource | rightsizing | reserved_instance | auto_scaling
    title: str
    description: str
    current_cost: float
    estimated_savings: float
    effort_level: str         # low | medium | high
    risk_level: str           # low | medium | high
    status: str               # active | dismissed | applied
    ai_summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationsResponse(BaseModel):
    items: List[RecommendationItem]
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
    daily_trend: List[DailyCostItem]
    service_breakdown: List[ServiceCostItem]
    region_breakdown: List[RegionCostItem]


# ── Service-wise Costs Response ───────────────────────────────────────────────

class ServiceCostsResponse(BaseModel):
    services: List[ServiceCostItem]
    total_cost: float


# ── AI Cost Analysis Response ─────────────────────────────────────────────────

class CostAnalyzeResponse(BaseModel):
    cost_summary: str
    highest_cost_services: List[str]
    idle_resources: List[str]
    wasted_resources: List[str]
    optimization_suggestions: List[str]
    reserved_instance_recommendations: List[str]
    auto_scaling_recommendations: List[str]
    estimated_monthly_savings: float
    recommendations: List[RecommendationItem]
    efficiency_score: int
    analyzed_at: datetime
