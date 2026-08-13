from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ReliabilityOverviewResponse(BaseModel):
    overall_reliability_score: float = Field(..., example=92.5)
    services_healthy: int = Field(..., example=5)
    services_at_risk: int = Field(..., example=2)
    services_breached: int = Field(..., example=1)
    slo_compliance_pct: float = Field(..., example=98.5)
    critical_burn_rates_count: int = Field(..., example=1)
    error_budget_remaining_pct: float = Field(..., example=84.5)
    mode_indicator: str = Field(..., example="LOCAL FIXTURE TELEMETRY MODE")


class MultiWindowBurnRateItem(BaseModel):
    window: str = Field(..., example="1h")
    burn_rate_x: float = Field(..., example=3.2)
    severity: str = Field(..., example="ELEVATED")
    explanation: str = Field(..., example="Burn rate at 3.2x over 1h window.")


class BurnRateOverviewResponse(BaseModel):
    service: str = Field(..., example="api-gateway")
    base_burn_rate_x: float = Field(..., example=1.0)
    multi_window_burn_rates: dict[str, MultiWindowBurnRateItem] = Field(default_factory=dict)


class ServiceReliabilityResponse(BaseModel):
    service_id: str = Field(..., example="api-gateway")
    service_name: str = Field(..., example="api-gateway")
    provider: str = Field(..., example="AWS")
    region: str = Field(..., example="us-east-1")
    availability_pct: float = Field(..., example=99.98)
    latency_p95_ms: float = Field(..., example=38.0)
    latency_p99_ms: float = Field(..., example=72.0)
    error_rate_pct: float = Field(..., example=0.02)
    slo_target: float = Field(..., example=99.9)
    current_slo: float = Field(..., example=99.98)
    error_budget_total_sec: float = Field(..., example=2592.0)
    error_budget_remaining_sec: float = Field(..., example=2073.6)
    error_budget_consumed_pct: float = Field(..., example=20.0)
    error_budget_remaining_pct: float = Field(..., example=80.0)
    burn_rate: float = Field(..., example=1.0)
    reliability_score: float = Field(..., example=95.0)
    risk_score: float = Field(..., example=12.0)
    risk_level: str = Field(..., example="LOW")
    status: str = Field(..., example="HEALTHY")
    top_recommendation: str = Field(..., example="Monitor service metric trends.")


class ErrorBudgetOverviewResponse(BaseModel):
    service_name: str = Field(..., example="api-gateway")
    target_slo: float = Field(..., example=99.9)
    total_budget_sec: float = Field(..., example=2592.0)
    consumed_budget_sec: float = Field(..., example=518.4)
    remaining_budget_sec: float = Field(..., example=2073.6)
    consumed_budget_pct: float = Field(..., example=20.0)
    remaining_budget_pct: float = Field(..., example=80.0)
    burn_rate_multiplier: float = Field(..., example=1.0)
    status: str = Field(..., example="HEALTHY")


class ReliabilityRiskResponse(BaseModel):
    service_name: str = Field(..., example="payment-service")
    risk_score: float = Field(..., example=78.5)
    risk_level: str = Field(..., example="CRITICAL")
    top_factors: list[str] = Field(default_factory=list)


class SloForecastResponse(BaseModel):
    forecast_status: str = Field(..., example="VALID")
    target_slo: float = Field(..., example=99.9)
    current_availability_pct: float = Field(..., example=99.98)
    projected_7_day_slo_pct: float | None = Field(default=99.95)
    projected_30_day_slo_pct: float | None = Field(default=99.92)
    projected_month_end_slo_pct: float | None = Field(default=99.92)
    projected_budget_consumed_pct: float = Field(..., example=25.0)
    days_to_exhaustion: int = Field(..., example=999)
    projected_exhaustion_date: str = Field(..., example="N/A (Budget Healthy)")
    is_compliant_projected: bool = Field(..., example=True)
    confidence_pct: float = Field(..., example=94.5)


class DependencyImpactResponse(BaseModel):
    service_name: str = Field(..., example="Checkout API")
    upstream_dependencies: list[str] = Field(default_factory=list)
    downstream_dependencies: list[str] = Field(default_factory=list)
    dependency_health: str = Field(..., example="DEGRADED")
    dependency_correlation: str = Field(..., example="PostgreSQL latency spike affecting payment processing.")


class ReliabilityIncidentResponse(BaseModel):
    incident_id: str = Field(..., example="INC-9482")
    title: str = Field(..., example="High P95 Latency Spike on Payment Service")
    service: str = Field(..., example="payment-service")
    severity: str = Field(..., example="HIGH")
    slo_impact: str = Field(..., example="Deducted 1.5% from 30d availability")
    error_budget_impact: str = Field(..., example="Consumed 320s of error budget")
    duration_minutes: int = Field(..., example=42)
    status: str = Field(..., example="INVESTIGATING")


class ReliabilityRecommendationResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service: str = Field(..., example="payment-service")
    priority: str = Field(..., example="CRITICAL")
    category: str = Field(..., example="Error Budget Preservation")
    reason: str = Field(..., example="High P95 latency limit breached.")
    evidence: str = Field(..., example="P95 latency = 780ms vs 500ms threshold.")
    recommended_action: str = Field(..., example="Scale database connection pool and enable Redis caching.")
    expected_reliability_impact: str = Field(..., example="Reduce P95 latency below 300ms.")


class ReliabilityAnalyzeResponse(BaseModel):
    analysis_engine: str = Field(..., example="Local Reliability Intelligence")
    badge: str = Field(..., example="Local Reliability Intelligence")
    is_ai_powered: bool = Field(..., example=False)
    executive_summary: str = Field(..., example="Platform SRE Reliability Score is 92.5/100.")
    critical_services: list[str] = Field(default_factory=list)
    recommendations: list[ReliabilityRecommendationResponse] = Field(default_factory=list)
    analyzed_at: str = Field(..., example="2026-08-14 05:00:00")


class ServiceDetailResponse(BaseModel):
    profile: ServiceReliabilityResponse
    error_budget: ErrorBudgetOverviewResponse
    multi_window_burn_rates: dict[str, MultiWindowBurnRateItem]
    forecast: SloForecastResponse
    dependencies: DependencyImpactResponse
    incidents: list[ReliabilityIncidentResponse] = Field(default_factory=list)
    anomalies_count: int = Field(default=0)
    capacity_risk: str = Field(default="LOW")
    security_risk_score: float = Field(default=15.0)
    cost_impact_monthly: float = Field(default=1250.0)
    recommendations: list[ReliabilityRecommendationResponse] = Field(default_factory=list)
