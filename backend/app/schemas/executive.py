"""
Pydantic Schemas for Executive Cloud Operations Command Center.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ── Health Score & Components ──────────────────────────────────────────────────


class ComponentScore(BaseModel):
    name: str
    score: int
    weight_pct: int
    status: str  # OPTIMAL, ACCEPTABLE, RISK, CRITICAL
    details: str


class HealthScoreResponse(BaseModel):
    overall_score: int
    reliability_score: int
    security_score: int
    cost_score: int
    performance_score: int
    capacity_score: int
    governance_score: int
    incident_health: int
    risk_level: str  # HEALTHY, LOW_RISK, MODERATE_RISK, HIGH_RISK, CRITICAL
    trend: str  # IMPROVING, STABLE, WORSENING, INSUFFICIENT_DATA
    components: list[ComponentScore]
    explanation: str


# ── Executive Summary ──────────────────────────────────────────────────────────


class ExecutiveSummaryResponse(BaseModel):
    summary_text: str
    source: str  # AI-powered Summary | Local Operations Intelligence
    generated_at: datetime
    key_highlights: list[str]


# ── Key Executive Metrics ──────────────────────────────────────────────────────


class KeyExecutiveMetricsResponse(BaseModel):
    active_incidents: int
    critical_incidents: int
    unresolved_anomalies: int
    security_findings: int
    critical_security_findings: int
    current_monthly_spend: float
    projected_spend: float
    potential_savings: float
    budget_utilization_pct: float
    capacity_risk_score: int
    policy_violations: int
    pending_remediations: int
    unhealthy_services: int
    kubernetes_risk_level: str


# ── Top Priorities Queue ───────────────────────────────────────────────────────


class ExecutivePriorityItem(BaseModel):
    id: str
    priority_score: float
    priority_level: str  # P0, P1, P2, P3
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    domain: str  # INCIDENT, SECURITY, FINOPS, CAPACITY, PERFORMANCE, GOVERNANCE, KUBERNETES
    title: str
    description: str
    affected_resource: str
    business_impact: str
    financial_impact: str
    recommended_action: str
    status: str
    created_at: datetime


class ExecutivePriorityListResponse(BaseModel):
    priorities: list[ExecutivePriorityItem]
    total: int
    p0_count: int
    p1_count: int


# ── Operational Trends ─────────────────────────────────────────────────────────


class OperationalTrendItem(BaseModel):
    metric_name: str
    domain: str
    current_period: float
    previous_period: float
    percentage_change: float | None = None
    direction: str  # UP, DOWN, NEUTRAL
    trend_status: str  # IMPROVING, STABLE, WORSENING, INSUFFICIENT_DATA
    unit: str


class OperationalTrendsResponse(BaseModel):
    trends: list[OperationalTrendItem]


# ── Cloud Provider Health ──────────────────────────────────────────────────────


class ProviderHealthItem(BaseModel):
    provider: str  # AWS, Azure, GCP, Kubernetes
    health_score: int
    monthly_spend: float
    active_incidents: int
    security_risk_level: str
    capacity_risk_score: int
    policy_violations: int
    service_count: int
    trend: str


class CloudProviderHealthResponse(BaseModel):
    providers: list[ProviderHealthItem]


# ── Service Health Map ─────────────────────────────────────────────────────────


class ServiceHealthItem(BaseModel):
    id: str
    name: str
    status: str  # HEALTHY, DEGRADED, CRITICAL, UNKNOWN
    environment: str
    provider: str
    incident_count: int
    anomaly_count: int
    monthly_cost: float
    security_findings_count: int
    capacity_risk: str
    dependencies_count: int
    last_updated: datetime


class ServiceHealthMapResponse(BaseModel):
    services: list[ServiceHealthItem]
    healthy_count: int
    degraded_count: int
    critical_count: int


# ── Cloud Risk Matrix ──────────────────────────────────────────────────────────


class RiskMatrixItem(BaseModel):
    domain: str  # Reliability, Security, FinOps, Capacity, Governance, Kubernetes, Performance
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    severity: str
    trend: str
    impact_summary: str
    recommended_action: str


class CloudRiskMatrixResponse(BaseModel):
    matrix: list[RiskMatrixItem]


# ── What Changed (Delta) ───────────────────────────────────────────────────────


class ChangeItem(BaseModel):
    category: str
    metric: str
    current_value: str
    previous_value: str
    change_type: str  # INCREASE, DECREASE, NEW, RESOLVED, UNCHANGED
    significance: str  # HIGH, MEDIUM, LOW


class WhatChangedResponse(BaseModel):
    changes: list[ChangeItem]
    period_days: int = 30


# ── Executive Timeline ─────────────────────────────────────────────────────────


class ExecutiveTimelineEvent(BaseModel):
    id: str
    timestamp: datetime
    domain: str
    severity: str
    title: str
    resource: str
    status: str
    details: str | None = None


class ExecutiveTimelineResponse(BaseModel):
    events: list[ExecutiveTimelineEvent]
    total: int


# ── Executive Alerts & Recommendations ─────────────────────────────────────────


class ExecutiveAlertItem(BaseModel):
    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    domain: str
    title: str
    message: str
    timestamp: datetime


class ExecutiveAlertsResponse(BaseModel):
    alerts: list[ExecutiveAlertItem]


class ExecutiveRecommendationItem(BaseModel):
    id: str
    domain: str
    action: str
    title: str
    impact: str
    risk_level: str
    estimated_savings: float | None = None
    suggested_owner: str
    status: str  # OPEN, IN_PROGRESS, COMPLETED


class ExecutiveRecommendationsResponse(BaseModel):
    recommendations: list[ExecutiveRecommendationItem]


# ── Executive Overview Aggregation Response ────────────────────────────────────


class ExecutiveOverviewResponse(BaseModel):
    health_score: HealthScoreResponse
    summary: ExecutiveSummaryResponse
    metrics: KeyExecutiveMetricsResponse
    top_priorities: list[ExecutivePriorityItem]
    provider_health: list[ProviderHealthItem]
    operational_trends: list[OperationalTrendItem]
    risk_matrix: list[RiskMatrixItem]
    what_changed: list[ChangeItem]
    alerts: list[ExecutiveAlertItem]
    mode_indicator: str = Field(
        default="DEMO / LOCAL MODE — Executive Intelligence Operating on Real Aggregated Platform Data",
        description="Execution mode indicator",
    )
