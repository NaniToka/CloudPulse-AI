"""
Pydantic schemas for the Enterprise Cloud Cost Optimizer & FinOps Intelligence module.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

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


class ProviderCostItem(BaseModel):
    provider: str
    cost: float
    percentage: float
    resource_count: int


class ProviderCostsResponse(BaseModel):
    providers: list[ProviderCostItem]
    total_cost: float


class RegionCostsResponse(BaseModel):
    regions: list[RegionCostItem]
    total_cost: float


# ── Cloud Cost Resource Item ──────────────────────────────────────────────────


class CloudCostItem(BaseModel):
    id: uuid.UUID
    resource_name: str
    service: str
    provider: str
    region: str
    cost: float = Field(..., ge=0.0)
    daily_cost: float = Field(default=0.0, ge=0.0)
    usage_amount: float = Field(default=0.0, ge=0.0)
    usage_unit: str
    environment: str
    status: str
    tags: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime

    model_config = {"from_attributes": True}


class CloudCostCreate(BaseModel):
    resource_name: str = Field(..., min_length=1, max_length=255)
    service: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., min_length=1, max_length=50)
    region: str = Field(default="us-central1", min_length=1, max_length=100)
    cost: float = Field(..., ge=0.0, description="Monthly cost must be non-negative")
    daily_cost: float = Field(default=0.0, ge=0.0)
    usage_amount: float = Field(default=0.0, ge=0.0)
    usage_unit: str = Field(default="hrs")
    environment: str = Field(default="production")
    status: str = Field(default="active")
    tags: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in ("aws", "azure", "gcp", "google", "k8s", "kubernetes", "other"):
            raise ValueError("Provider must be one of: aws, azure, gcp, kubernetes, other")
        return cleaned


class CloudCostListResponse(BaseModel):
    items: list[CloudCostItem]
    total: int


# ── Optimization Recommendation Item ─────────────────────────────────────────


class RecommendationItem(BaseModel):
    id: uuid.UUID
    resource_id: uuid.UUID | None = None
    resource_name: str
    service: str
    recommendation_type: str  # idle_resource | wasted_resource | rightsizing | reserved_instance | auto_scaling
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
    provider_breakdown: list[ProviderCostItem] = Field(default_factory=list)
    data_source: str = Field(default="Demo Data — No Cloud Credentials Connected", description="Data source indicator")
    environment: str = Field(default="Local Development", description="Execution environment")


class CostTrendsResponse(BaseModel):
    daily_trend: list[DailyCostItem]
    monthly_trend: list[DailyCostItem] = Field(default_factory=list)
    projected_cost: float
    trend_direction: str


# ── Service-wise Costs Response ───────────────────────────────────────────────


class ServiceCostsResponse(BaseModel):
    services: list[ServiceCostItem]
    total_cost: float


# ── Cost Anomaly Response ─────────────────────────────────────────────────────


class CostAnomalyItem(BaseModel):
    id: str
    anomaly_score: float
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    detected_date: str
    provider: str
    service: str
    resource: str
    expected_cost: float
    actual_cost: float
    difference: float
    explanation: str


class CostAnomaliesResponse(BaseModel):
    anomalies: list[CostAnomalyItem]
    total_anomalies: int
    critical_anomalies: int


# ── Cost Forecast Response ────────────────────────────────────────────────────


class CostForecastResponse(BaseModel):
    forecast_7_day: float
    forecast_30_day: float
    projected_month_end: float
    confidence: float
    historical_basis: str
    trend_direction: str


# ── Cost Budget Models ────────────────────────────────────────────────────────


class CostBudgetItem(BaseModel):
    id: uuid.UUID
    name: str
    provider: str
    service: str
    environment: str
    amount: float
    current_spend: float = 0.0
    utilization_pct: float = 0.0
    projected_spend: float = 0.0
    remaining: float = 0.0
    period: str
    threshold_status: str  # NORMAL | WARNING_50 | WARNING_75 | CRITICAL_90 | EXCEEDED_100
    threshold_percentages: list[int] = Field(default_factory=lambda: [50, 75, 90, 100])
    thresholds_reached: list[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CostBudgetPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0.0)
    provider: str = Field(default="all")
    service: str = Field(default="all")
    environment: str = Field(default="all")
    period: str = Field(default="monthly")
    threshold_percentages: list[int] = Field(default_factory=lambda: [50, 75, 90, 100])

    @field_validator("threshold_percentages")
    @classmethod
    def validate_thresholds(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("threshold_percentages cannot be empty")
        for val in v:
            if val < 1 or val > 100:
                raise ValueError(f"Threshold percentage {val} must be between 1 and 100")
        return sorted(list(set(v)))


class CostBudgetListResponse(BaseModel):
    budgets: list[CostBudgetItem]
    total: int


# ── Savings & Optimization Summary ─────────────────────────────────────────────


class CostSavingsResponse(BaseModel):
    total_monthly_savings: float
    total_annual_savings: float  # monthly * 12
    opportunity_count: int


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
    analysis_engine: str = Field(default="Local FinOps Intelligence")


# ── Executive FinOps Intelligence & Reporting Schemas ─────────────────────────


class CostHealthScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    status: str  # Healthy | Watch | At Risk | Critical
    factors: list[str]
    explanation: str


class ExecutiveCostSummaryResponse(BaseModel):
    monthly_cost: float
    previous_month_cost: float
    percentage_change: float
    summary_statements: list[str]


class CostDriverItem(BaseModel):
    name: str
    cost: float = 0.0
    reason: str


class CostDriversResponse(BaseModel):
    top_provider: CostDriverItem
    top_service: CostDriverItem
    top_region: CostDriverItem
    top_resource: CostDriverItem
    fastest_growing_service: CostDriverItem
    largest_anomaly: dict[str, Any]
    largest_savings_opportunity: dict[str, Any]


class ProviderPeriodChange(BaseModel):
    provider: str
    current_cost: float
    previous_cost: float
    difference: float


class ServicePeriodChange(BaseModel):
    service: str
    current_cost: float
    previous_cost: float
    difference: float


class PeriodComparisonResponse(BaseModel):
    current_spend: float
    previous_spend: float
    total_spend_difference: float
    percentage_difference: float
    provider_changes: list[ProviderPeriodChange]
    service_changes: list[ServicePeriodChange]


class CostExplorerNode(BaseModel):
    id: str
    name: str
    level: str  # provider | service | region | resource
    cost: float
    percentage_of_total: float
    resource_count: int = 1
    children: list[CostExplorerNode] = Field(default_factory=list)


class CostExplorerResponse(BaseModel):
    nodes: list[CostExplorerNode]
    total_cost: float


class SavingsBreakdownItem(BaseModel):
    key: str
    savings: float


class SavingsCenterResponse(BaseModel):
    total_monthly_savings: float
    total_annual_savings: float  # monthly * 12
    opportunity_count: int
    average_savings_per_opportunity: float
    by_provider: list[dict[str, Any]]
    by_category: list[dict[str, Any]]
    by_service: list[dict[str, Any]]


class FinOpsReportRequest(BaseModel):
    date_range: str = Field(default="30_days")  # 7_days | 30_days | current_month | custom
    provider: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class FinOpsReportResponse(BaseModel):
    generated_at: str
    date_range: str
    data_source: str
    health_score: CostHealthScoreResponse
    executive_summary: str
    summary_statements: list[str]
    total_monthly_cost: float
    previous_month_cost: float
    percentage_change: float
    projected_cost: float
    potential_monthly_savings: float
    potential_annual_savings: float
    cost_drivers: CostDriversResponse
    period_comparison: PeriodComparisonResponse
    provider_breakdown: list[ProviderCostItem]
    service_breakdown: list[ServiceCostItem]
    region_breakdown: list[RegionCostItem]
    anomalies: list[CostAnomalyItem]
    forecast: CostForecastResponse
    budget_status: dict[str, Any]
    budget_crossing_projection: dict[str, Any]
    savings_center: SavingsCenterResponse
    recommendations: list[RecommendationItem]

