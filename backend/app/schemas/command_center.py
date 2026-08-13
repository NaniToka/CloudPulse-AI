"""
Pydantic Schemas for Enterprise Executive Intelligence & Operations Command Center.
"""

from __future__ import annotations

from pydantic import BaseModel

# ── 1. Health & Risk Scores ───────────────────────────────────────────────────


class ExecutiveHealthResponse(BaseModel):
    overall_health_score: float
    status: str  # HEALTHY, DEGRADED, AT_RISK, CRITICAL
    base_score: float
    penalty: float
    contributing_factors: list[str]
    slo_compliance_pct: float
    security_score: float
    finops_score: float
    capacity_health: float
    active_breaches: int


class OperationalRiskResponse(BaseModel):
    operational_risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    active_risk_factors_count: int
    affected_services_count: int
    affected_services: list[str]


# ── 2. Insights & Brief ────────────────────────────────────────────────────────


class IntelligenceInsightResponse(BaseModel):
    id: str
    timestamp: str
    category: str
    severity: str
    title: str
    summary: str
    affected_service: str | None = None
    affected_provider: str | None = None
    affected_region: str | None = None
    business_impact: str
    technical_impact: str
    confidence: float
    recommended_action: str
    source_system: str


class ExecutiveBriefResponse(BaseModel):
    summary: str
    top_concern: str
    business_impact: str
    recommended_action: str
    is_ai_powered: bool
    badge: str


# ── 3. Risks, Opportunities & Trends ─────────────────────────────────────────


class TopRiskItem(BaseModel):
    rank: int
    title: str
    severity: str
    score: float
    affected_service: str
    reason: str
    impact: str
    recommended_action: str


class TopOpportunityItem(BaseModel):
    id: str
    title: str
    source: str
    impact: str
    potential_savings_monthly: float | None = None
    recommended_action: str
    priority: str


class ExecutiveTrendItem(BaseModel):
    metric: str
    current: float
    previous_period: float
    percentage_change: float
    trend_direction: str  # IMPROVING, STABLE, DEGRADING


class TimelineItem(BaseModel):
    timestamp: str
    event: str
    service: str
    severity: str
    source: str
    impact: str


# ── 4. Aggregated Overview Response ───────────────────────────────────────────


class CommandCenterOverviewResponse(BaseModel):
    health: ExecutiveHealthResponse
    risk: OperationalRiskResponse
    brief: ExecutiveBriefResponse
    insights: list[IntelligenceInsightResponse]
    top_risks: list[TopRiskItem]
    opportunities: list[TopOpportunityItem]
    timeline: list[TimelineItem]
    trends: list[ExecutiveTrendItem]
    active_incidents_count: int
    monthly_spend: float
    potential_savings: float


class CommandCenterAnalyzeResponse(BaseModel):
    overview: CommandCenterOverviewResponse
    analysis_summary: str
    correlated_insights_count: int
