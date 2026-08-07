"""
Pydantic v2 schemas for Incident Management Center.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IncidentSeverity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class IncidentStatus(str, Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    MONITORING = "Monitoring"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class IncidentPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500, description="Title of the incident")
    description: str | None = Field(None, description="Detailed description of the incident")
    severity: IncidentSeverity = Field(
        default=IncidentSeverity.P2, description="Severity level P0-P3"
    )
    priority: IncidentPriority = Field(default=IncidentPriority.HIGH, description="Priority level")
    status: IncidentStatus = Field(
        default=IncidentStatus.OPEN, description="Current lifecycle status"
    )
    affected_service: str | None = Field(
        default="api-gateway", description="Primary affected service"
    )
    affected_services: list[str] = Field(
        default_factory=list, description="List of affected services"
    )
    affected_region: str | None = Field(default="us-east-1", description="Affected cloud region")
    assigned_engineer: str | None = Field(None, description="Engineer assigned to the incident")
    assigned_to: str | None = Field(None, description="Assignee name or email")


class IncidentCreate(IncidentBase):
    created_by: str | None = Field(
        default="System User", description="User who opened the incident"
    )
    started_at: datetime | None = Field(None, description="Time incident started")
    auto_analyze: bool = Field(
        default=True, description="Whether to trigger Gemini AI analysis immediately"
    )


class IncidentUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=500)
    description: str | None = None
    severity: IncidentSeverity | None = None
    priority: IncidentPriority | None = None
    status: IncidentStatus | None = None
    affected_service: str | None = None
    affected_services: list[str] | None = None
    affected_region: str | None = None
    assigned_engineer: str | None = None
    assigned_to: str | None = None
    resolution_notes: str | None = None


class IncidentResolve(BaseModel):
    resolution_notes: str = Field(
        ..., min_length=5, description="Summary of how the incident was resolved"
    )
    resolved_by: str | None = Field(
        default="Engineer", description="User or automated agent resolving the incident"
    )


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
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: str | None = None
    started_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
    resolved_by: str | None = None

    # AI Fields
    ai_summary: str | None = None
    root_cause: str | None = None
    ai_root_cause: str | None = None
    ai_business_impact: str | None = None
    ai_suggested_resolution: str | None = None
    ai_immediate_mitigation: str | None = None
    ai_long_term_prevention: list[str] | None = Field(default_factory=list)
    ai_preventive_actions: list[str] | None = Field(default_factory=list)
    ai_similar_incidents: list[dict[str, Any]] | None = Field(default_factory=list)
    ai_estimated_resolution_time: str | None = None
    ai_confidence_score: float | None = 0.94


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
