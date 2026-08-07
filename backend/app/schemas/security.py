"""
Pydantic v2 schemas for AI Security & Cloud Compliance Center.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SecurityFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_name: str
    provider: str
    region: str
    resource: str
    severity: str  # Critical, High, Medium, Low
    category: str  # IAM, Network, Storage, Database, Secrets
    compliance_framework: str
    description: str
    recommendation: str
    ai_analysis: dict[str, Any] | None = None
    status: str  # Open, In_Progress, Resolved, Ignored
    created_at: datetime
    updated_at: datetime


class SecurityScanPayload(BaseModel):
    provider: str | None = Field("AWS", description="Cloud Provider (AWS, GCP, Azure)")
    scan_name: str | None = Field("Cloud Security Audit Scan", description="Scan execution name")


class SecurityScanResponse(BaseModel):
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    scanned_resources: int
    overall_security_score: float
    message: str


class ComplianceReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    framework: str
    overall_score: float
    passed_controls: int
    failed_controls: int
    total_controls: int
    category_scores: dict[str, float] = Field(default_factory=dict)
    created_at: datetime


class RiskScoreResponse(BaseModel):
    overall_security_score: float  # 0 to 100
    overall_risk_score: float  # 0.0 to 10.0
    critical_findings_count: int
    high_findings_count: int
    resources_at_risk_count: int
    compliance_overall_percentage: float
    risk_trend: list[dict[str, Any]] = Field(default_factory=list)
    severity_distribution: dict[str, int] = Field(default_factory=dict)


class SecurityListResponse(BaseModel):
    items: list[SecurityFindingResponse]
    total: int
    page: int
    size: int
    pages: int
