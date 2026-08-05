"""
Pydantic v2 schemas for Incident Management Center.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
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
    description: Optional[str] = Field(None, description="Detailed description of the incident")
    severity: IncidentSeverity = Field(default=IncidentSeverity.P2, description="Severity level P0-P3")
    priority: IncidentPriority = Field(default=IncidentPriority.HIGH, description="Priority level")
    status: IncidentStatus = Field(default=IncidentStatus.OPEN, description="Current lifecycle status")
    affected_service: Optional[str] = Field(default="api-gateway", description="Primary affected service")
    affected_services: List[str] = Field(default_factory=list, description="List of affected services")
    assigned_engineer: Optional[str] = Field(None, description="Engineer assigned to the incident")


class IncidentCreate(IncidentBase):
    created_by: Optional[str] = Field(default="System User", description="User who opened the incident")
    auto_analyze: bool = Field(default=True, description="Whether to trigger Gemini AI analysis immediately")


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    affected_service: Optional[str] = None
    affected_services: Optional[List[str]] = None
    assigned_engineer: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentResolve(BaseModel):
    resolution_notes: str = Field(..., min_length=5, description="Summary of how the incident was resolved")
    resolved_by: Optional[str] = Field(default="Engineer", description="User or automated agent resolving the incident")


class IncidentAIAnalysisResponse(BaseModel):
    ai_summary: str
    ai_root_cause: str
    ai_business_impact: str
    ai_suggested_resolution: str
    ai_preventive_actions: List[str]
    ai_similar_incidents: List[dict[str, Any]]
    ai_estimated_resolution_time: str


class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None

    # AI Fields
    ai_summary: Optional[str] = None
    ai_root_cause: Optional[str] = None
    ai_business_impact: Optional[str] = None
    ai_suggested_resolution: Optional[str] = None
    ai_preventive_actions: Optional[List[str]] = Field(default_factory=list)
    ai_similar_incidents: Optional[List[dict[str, Any]]] = Field(default_factory=list)
    ai_estimated_resolution_time: Optional[str] = None


class IncidentListResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    size: int
    pages: int


class SeverityCount(BaseModel):
    severity: str
    count: int


class MonthlyTrendPoint(BaseModel):
    month: str
    count: int
    resolved_count: int


class IncidentAnalyticsResponse(BaseModel):
    incidents_by_severity: List[SeverityCount]
    mean_time_to_resolve_minutes: float
    monthly_trend: List[MonthlyTrendPoint]
    resolution_rate_percent: float
    active_incidents: int
    resolved_incidents: int
    total_incidents: int
