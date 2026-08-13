"""
Pydantic Schemas for Enterprise SLO, SLA & Error Budget Intelligence Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# ── 1. SLO Objectives ─────────────────────────────────────────────────────────


class SloObjectiveCreate(BaseModel):
    service: str
    name: str
    description: str | None = None
    indicator_type: str = Field(default="availability")  # availability, latency, error_rate, throughput
    target: float = Field(default=99.9, ge=0.0, le=100.0)
    target_threshold_ms: float | None = None
    window: str = Field(default="30d")
    enabled: bool = True


class SloObjectiveUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target: float | None = None
    target_threshold_ms: float | None = None
    window: str | None = None
    enabled: bool | None = None


class SloObjectiveResponse(BaseModel):
    id: uuid.UUID
    service: str
    name: str
    description: str | None
    indicator_type: str
    target: float
    target_threshold_ms: float | None
    window: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── 2. Indicators & Measurements ─────────────────────────────────────────────


class SliMetricsResponse(BaseModel):
    service: str
    indicator_type: str
    total_events: int
    good_events: int
    bad_events: int
    availability_pct: float
    error_rate_pct: float
    latency_p50_ms: float
    latency_p90_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_rps: float
    window: str
    status: str


# ── 3. Error Budget & Burn Rate ───────────────────────────────────────────────


class ErrorBudgetResponse(BaseModel):
    service: str
    target_slo: float
    window_days: int
    total_budget_sec: float
    consumed_budget_sec: float
    remaining_budget_sec: float
    consumed_budget_pct: float
    remaining_budget_pct: float
    burn_rate_multiplier: float
    status: str


class BurnRateResponse(BaseModel):
    service: str
    burn_rate_x: float
    severity: str  # NORMAL, ELEVATED, HIGH, CRITICAL
    window_hours: int
    observed_failure_rate: float
    allowed_failure_rate: float
    explanation: str


# ── 4. Violations & Incidents ──────────────────────────────────────────────────


class SloViolationResponse(BaseModel):
    id: str
    service: str
    violation_type: str
    severity: str
    target_value: float
    actual_value: float
    difference: float
    duration_seconds: int
    explanation: str
    status: str
    incident_id: str | None = None


class CorrelatedIncidentResponse(BaseModel):
    incident_id: str
    title: str
    service: str
    severity: str
    status: str
    slo_impact: str
    estimated_downtime_sec: int
    error_budget_consumed_pct: float
    created_at: str


# ── 5. Reliability, Forecast & Overview ───────────────────────────────────────


class ServiceReliabilityResponse(BaseModel):
    service: str
    scenario: str
    indicator_type: str
    target_slo: float
    availability_pct: float
    error_rate_pct: float
    latency_p95_ms: float
    throughput_rps: float
    reliability_score: float
    status: str
    contributing_factors: list[str]


class SloForecastResponse(BaseModel):
    service: str
    target_slo: float
    current_availability_pct: float
    projected_month_end_slo_pct: float
    projected_budget_consumed_pct: float
    projected_remaining_budget_pct: float
    days_to_exhaustion: int
    projected_exhaustion_date: str
    is_compliant_projected: bool
    confidence_pct: float


class SloOverviewResponse(BaseModel):
    platform_reliability_score: float
    slo_compliance_pct: float
    total_services: int
    healthy_services: int
    at_risk_services: int
    breached_services: int
    active_violations: int
    average_error_budget_remaining_pct: float
    mode_indicator: str


class SloRecommendationResponse(BaseModel):
    id: str
    service: str
    problem: str
    impact: str
    recommendation: str
    priority: str  # HIGH, MEDIUM, LOW
    expected_improvement: str


class SloAnalyzeResponse(BaseModel):
    overview: SloOverviewResponse
    services_analyzed: int
    critical_breaches_count: int
    recommendations: list[SloRecommendationResponse]
    analysis_summary: str
