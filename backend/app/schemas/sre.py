"""
Pydantic schemas for Enterprise SRE & Reliability Intelligence Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# ── SLI & SLO Schemas ─────────────────────────────────────────────────────────


class SliMetricsItem(BaseModel):
  total_requests: int
  failed_requests: int
  availability: float
  error_rate: float
  latency_p50_ms: float
  latency_p95_ms: float
  latency_p99_ms: float
  throughput_rps: float


class SloItem(BaseModel):
  id: uuid.UUID
  service: str
  name: str
  description: str | None = None
  indicator_type: str  # availability | latency | error_rate | throughput
  target: float
  target_threshold_ms: float | None = None
  window: str  # 30d | 7d | 24h | 1h
  enabled: bool
  current_sli: float = 0.0
  compliance_percentage: float = 100.0
  status: str  # HEALTHY | AT_RISK | BREACHED
  created_at: datetime
  updated_at: datetime

  model_config = {"from_attributes": True}


class SloCreatePayload(BaseModel):
  service: str = Field(..., min_length=2)
  name: str = Field(..., min_length=3)
  description: str | None = None
  indicator_type: str = Field(default="availability")
  target: float = Field(..., gt=0.0, le=100.0)
  target_threshold_ms: float | None = None
  window: str = Field(default="30d")
  enabled: bool = Field(default=True)


class SloUpdatePayload(BaseModel):
  name: str | None = None
  description: str | None = None
  target: float | None = None
  target_threshold_ms: float | None = None
  window: str | None = None
  enabled: bool | None = None


class SloListResponse(BaseModel):
  slos: list[SloItem]
  total: int


# ── Error Budget & Burn Rate Schemas ──────────────────────────────────────────


class ErrorBudgetItem(BaseModel):
  service: str
  target_slo: float
  total_budget_pct: float
  consumed_pct: float
  remaining_pct: float
  remaining_budget_units: float
  status: str  # HEALTHY | AT_RISK | EXHAUSTED


class BurnRateItem(BaseModel):
  service: str
  burn_1h: float
  burn_6h: float
  burn_24h: float
  burn_7d: float
  status: str  # NORMAL | ELEVATED | CRITICAL


# ── Service Reliability Item & List ───────────────────────────────────────────


class ServiceReliabilityItem(BaseModel):
  service: str
  reliability_score: float
  rating: str  # EXCELLENT | GOOD | DEGRADED | CRITICAL
  availability: float
  latency_p95_ms: float
  error_rate: float
  throughput_rps: float
  slo_status: str  # HEALTHY | AT_RISK | BREACHED
  error_budget_remaining_pct: float
  burn_rate_status: str  # NORMAL | ELEVATED | CRITICAL
  active_incidents_count: int
  trend: str  # IMPROVING | STABLE | DEGRADED


class ServiceReliabilityListResponse(BaseModel):
  services: list[ServiceReliabilityItem]
  total: int


# ── Risk, Incident & Dependency Schemas ───────────────────────────────────────


class ReliabilityRiskItem(BaseModel):
  id: str
  risk: str
  severity: str  # CRITICAL | HIGH | MEDIUM | LOW
  service: str
  metric: str
  current_value: str
  threshold: str
  detected_at: str
  explanation: str
  recommended_action: str


class ReliabilityRiskListResponse(BaseModel):
  risks: list[ReliabilityRiskItem]
  total_risks: int
  critical_risks: int


class IncidentImpactItem(BaseModel):
  id: uuid.UUID
  title: str
  service: str
  severity: str
  status: str
  started_at: datetime | None = None
  duration_minutes: float = 0.0
  slo_impact: str
  budget_impact_pct: float


class IncidentImpactListResponse(BaseModel):
  incidents: list[IncidentImpactItem]
  total: int


class DependencyImpactItem(BaseModel):
  dependency: str
  target_service: str
  health: str  # HEALTHY | DEGRADED | CRITICAL
  latency_ms: float
  error_rate: float
  affected_services: list[str]
  reliability_risk: str


class DependencyImpactListResponse(BaseModel):
  dependencies: list[DependencyImpactItem]
  total: int


# ── Forecast & Recommendation Schemas ─────────────────────────────────────────


class ForecastPeriod(BaseModel):
  availability: float
  error_rate: float
  latency_ms: float
  slo_status: str


class ReliabilityForecastResponse(BaseModel):
  forecast_24h: ForecastPeriod
  forecast_7d: ForecastPeriod
  forecast_30d: ForecastPeriod
  confidence: float
  historical_basis: str
  status: str  # VALID | INSUFFICIENT_DATA


class SreRecommendationItem(BaseModel):
  id: str
  service: str
  category: str
  severity: str  # CRITICAL | HIGH | MEDIUM | LOW
  reason: str
  evidence: str
  recommended_action: str
  expected_impact: str
  confidence: float


class SreRecommendationListResponse(BaseModel):
  recommendations: list[SreRecommendationItem]
  total: int


# ── SRE Overview & AI Analysis Schemas ────────────────────────────────────────


class SreOverviewResponse(BaseModel):
  overall_score: float
  overall_rating: str
  services_healthy: int
  services_at_risk: int
  slo_breaches: int
  error_budget_remaining_avg: float
  active_incidents_count: int
  data_source: str = Field(
      default="Demo Data — No Production Telemetry Connected"
  )
  environment: str = Field(default="Local Development")


class SreAnalyzeResponse(BaseModel):
  executive_summary: str
  critical_services: list[str]
  error_budget_warnings: list[str]
  sre_recommendations: list[SreRecommendationItem]
  analyzed_at: str
  analysis_engine: str = Field(default="Local SRE Intelligence")
