"""
Pydantic v2 schemas for Enterprise Incident Intelligence & Root Cause Analysis Engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IncidentSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    # Legacy mappings
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    IDENTIFIED = "IDENTIFIED"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    # Legacy aliases
    OPEN = "Open"
    INVESTIGATING_LEGACY = "Investigating"
    MONITORING = "Monitoring"
    RESOLVED_LEGACY = "Resolved"
    CLOSED_LEGACY = "Closed"


class IncidentPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# ---------------------------------------------------------------------------
# Timeline Event Schemas
# ---------------------------------------------------------------------------


class IncidentTimelineEventBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_type: str = Field(
        default="metric_anomaly",
        description="Event type: metric_anomaly, alert_triggered, trace_failure, log_error, incident_created, rca_identified, remediation_recommended, remediation_executed, status_changed, engineer_note",
    )
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    source: str = Field(default="system")
    event_metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata")
    timestamp: datetime | None = None


class IncidentTimelineEventCreate(IncidentTimelineEventBase):
    pass


class IncidentTimelineEventResponse(IncidentTimelineEventBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    timestamp: datetime
    created_by: str | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Evidence & Recommended Actions Schemas
# ---------------------------------------------------------------------------


class IncidentEvidenceItem(BaseModel):
    type: str = Field(..., description="metric | log | trace | alert | topology | kubernetes | cloud")
    source: str = Field(..., description="Service, resource, or component name")
    message: str = Field(..., description="Evidence detail or excerpt")
    severity: str = Field(default="HIGH", description="CRITICAL | HIGH | MEDIUM | LOW")
    timestamp: datetime | None = None
    metric_value: float | None = None
    threshold: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class IncidentRecommendedAction(BaseModel):
    id: str = Field(..., description="Action ID, e.g. act-scale-redis")
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Detailed description")
    action_type: str = Field(default="config", description="scale | restart | config | circuit_breaker | rollback | runbook")
    workflow_id: str | None = Field(None, description="Optional workflow ID to trigger")
    automated: bool = Field(default=True, description="Whether can be automated after approval")
    risk_level: str = Field(default="LOW", description="CRITICAL | HIGH | MEDIUM | LOW")
    parameters: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Incident Base & CRUD Schemas
# ---------------------------------------------------------------------------


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500, description="Title of the incident")
    description: str | None = Field(None, description="Detailed description of the incident")
    severity: IncidentSeverity = Field(
        default=IncidentSeverity.HIGH, description="Severity level: CRITICAL, HIGH, MEDIUM, LOW (or P0-P3)"
    )
    priority: IncidentPriority = Field(default=IncidentPriority.HIGH, description="Priority level")
    status: IncidentStatus = Field(
        default=IncidentStatus.INVESTIGATING, description="Current lifecycle status"
    )
    source: str = Field(default="correlation_engine", description="Origin source")
    affected_service: str | None = Field(
        default="api-gateway", description="Primary affected service"
    )
    affected_services: list[str] = Field(
        default_factory=list, description="List of affected services"
    )
    affected_resources: list[str] = Field(
        default_factory=list, description="List of affected resources / hosts / pods"
    )
    affected_region: str | None = Field(default="us-east-1", description="Affected cloud region")
    assigned_engineer: str | None = Field(None, description="Engineer assigned to the incident")
    assigned_to: str | None = Field(None, description="Assignee name or email")


class IncidentCreate(IncidentBase):
    created_by: str | None = Field(
        default="System User", description="User who opened the incident"
    )
    started_at: datetime | None = Field(None, description="Time incident started")
    detected_at: datetime | None = Field(None, description="Time incident was detected")
    auto_analyze: bool = Field(
        default=True, description="Whether to trigger Gemini AI analysis and RCA immediately"
    )
    raw_alerts: list[dict[str, Any]] | None = Field(
        default=None, description="Optional raw alerts to correlate immediately"
    )


class IncidentUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=500)
    description: str | None = None
    severity: IncidentSeverity | None = None
    priority: IncidentPriority | None = None
    status: IncidentStatus | None = None
    source: str | None = None
    affected_service: str | None = None
    affected_services: list[str] | None = None
    affected_resources: list[str] | None = None
    affected_region: str | None = None
    assigned_engineer: str | None = None
    assigned_to: str | None = None
    resolution_notes: str | None = None


class IncidentAcknowledgeRequest(BaseModel):
    assigned_to: str | None = Field(default=None, description="Assignee taking ownership")
    notes: str | None = Field(default=None, description="Initial triage notes")


class IncidentResolve(BaseModel):
    resolution_notes: str = Field(
        ..., min_length=5, description="Summary of how the incident was resolved"
    )
    resolved_by: str | None = Field(
        default="Engineer", description="User or automated agent resolving the incident"
    )


# ---------------------------------------------------------------------------
# RCA & Blast Radius Schemas
# ---------------------------------------------------------------------------


class RootCauseAnalysisResponse(BaseModel):
    incident_id: uuid.UUID
    root_cause: str
    confidence: float
    evidence: list[IncidentEvidenceItem]
    affected_components: list[str]
    contributing_factors: list[str]
    recommended_actions: list[IncidentRecommendedAction]
    ai_summary: str | None = None
    ai_business_impact: str | None = None


class BlastRadiusResponse(BaseModel):
    incident_id: uuid.UUID
    root_component: str
    directly_affected_resources: list[str]
    indirectly_affected_resources: list[str]
    affected_services: list[str]
    dependency_depth: int
    estimated_user_impact: str  # CRITICAL | HIGH | MEDIUM | LOW
    financial_risk_estimate: str
    topology_graph: dict[str, Any] = Field(default_factory=dict)  # nodes and edges


# ---------------------------------------------------------------------------
# Correlation Schemas
# ---------------------------------------------------------------------------


class IncidentCorrelationRequest(BaseModel):
    alerts: list[dict[str, Any]] = Field(default_factory=list, description="Raw alerts to correlate")
    time_window_minutes: int = Field(default=15, ge=1, le=120)
    organization_id: uuid.UUID | None = None


class IncidentCorrelationResponse(BaseModel):
    correlated_incidents_count: int
    raw_alerts_processed: int
    incidents: list[IncidentResponse]


# ---------------------------------------------------------------------------
# Remediation Execution Schemas
# ---------------------------------------------------------------------------


class IncidentRemediateRequest(BaseModel):
    action_id: str = Field(..., description="Action ID to execute")
    authorized_by: str = Field(default="Engineer", description="Engineer authorizing execution")
    override_parameters: dict[str, Any] = Field(default_factory=dict)


class IncidentRemediateResponse(BaseModel):
    action_id: str
    status: str  # EXECUTED | AWAITING_APPROVAL | FAILED
    workflow_execution_id: str | None = None
    message: str
    executed_at: datetime


# ---------------------------------------------------------------------------
# Full Incident Response
# ---------------------------------------------------------------------------


class IncidentAIAnalysisResponse(BaseModel):
    ai_summary: str
    root_cause: str
    ai_root_cause: str
    ai_business_impact: str
    ai_suggested_resolution: str
    ai_immediate_mitigation: str
    ai_long_term_prevention: list[str]
    ai_preventive_actions: list[str]
    ai_similar_incidents: list[dict[str, Any]]
    ai_estimated_resolution_time: str
    ai_confidence_score: float


class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    created_by: str | None = None
    started_at: datetime | None = None
    detected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
    resolved_by: str | None = None

    # Analysis & Correlation Fields
    confidence_score: float = 0.94
    impact_score: float = 85.0
    root_cause: str | None = None
    contributing_factors: list[str] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    correlation_metadata: dict[str, Any] = Field(default_factory=dict)
    recommended_actions: list[dict[str, Any]] = Field(default_factory=list)
    blast_radius: dict[str, Any] = Field(default_factory=dict)

    # AI Fields
    ai_summary: str | None = None
    ai_root_cause: str | None = None
    ai_business_impact: str | None = None
    ai_suggested_resolution: str | None = None
    ai_immediate_mitigation: str | None = None
    ai_long_term_prevention: list[str] | None = Field(default_factory=list)
    ai_preventive_actions: list[str] | None = Field(default_factory=list)
    ai_similar_incidents: list[dict[str, Any]] | None = Field(default_factory=list)
    ai_estimated_resolution_time: str | None = None
    ai_confidence_score: float | None = 0.94

    # Timeline Events
    timeline_events: list[IncidentTimelineEventResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Incident List & Stats Response Schemas
# ---------------------------------------------------------------------------


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    page: int
    size: int
    pages: int


class IncidentStatsResponse(BaseModel):
    open_incidents: int
    critical_incidents: int
    avg_resolution_time_minutes: float
    sla_compliance_percent: float


class SeverityCount(BaseModel):
    severity: str
    count: int


class MonthlyTrendPoint(BaseModel):
    month: str
    count: int
    resolved_count: int


class IncidentAnalyticsResponse(BaseModel):
    incidents_by_severity: list[SeverityCount]
    mean_time_to_resolve_minutes: float
    monthly_trend: list[MonthlyTrendPoint]
    resolution_rate_percent: float
    active_incidents: int
    resolved_incidents: int
    total_incidents: int
    sla_compliance_percent: float
