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
    resource_type: str = "s3_bucket"
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # IAM, Network, Storage, Database, Secrets, Compute, Kubernetes
    compliance_framework: str
    description: str
    recommendation: str
    risk_score: float = 7.5
    confidence: float = 0.90
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    ai_analysis: dict[str, Any] | None = None
    status: str  # OPEN, INVESTIGATING, MITIGATED, RESOLVED, ACCEPTED_RISK
    first_detected_at: datetime | None = None
    last_detected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SecurityStatusUpdatePayload(BaseModel):
    status: str = Field(..., description="OPEN, INVESTIGATING, MITIGATED, RESOLVED, ACCEPTED_RISK")
    notes: str | None = Field(None, description="Optional triage/remediation notes")


class SecurityScanPayload(BaseModel):
    provider: str | None = Field("AWS", description="Cloud Provider (AWS, GCP, Azure, Kubernetes)")
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
    risk_level: str = "Low"
    critical_findings_count: int
    high_findings_count: int
    medium_findings_count: int = 0
    low_findings_count: int = 0
    resources_at_risk_count: int
    compliance_overall_percentage: float
    risk_trend: list[dict[str, Any]] = Field(default_factory=list)
    severity_distribution: dict[str, int] = Field(default_factory=dict)


class SecurityRecommendation(BaseModel):
    id: str
    title: str
    severity: str
    category: str
    resource: str
    action: str
    fix_time_estimate: str = "15 mins"
    compliance_framework: str


class SecurityOverviewResponse(BaseModel):
    posture_score: float
    overall_risk_score: float
    risk_level: str
    open_findings_count: int
    critical_findings_count: int
    high_findings_count: int
    medium_findings_count: int
    low_findings_count: int
    resources_at_risk_count: int
    compliance_scorecards: list[ComplianceReportResponse]
    top_recommendations: list[SecurityRecommendation]
    threat_vectors: list[dict[str, Any]] = Field(default_factory=list)


class SecurityListResponse(BaseModel):
    items: list[SecurityFindingResponse]
    total: int
    page: int
    size: int
    pages: int
