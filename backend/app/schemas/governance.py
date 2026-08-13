"""
Pydantic schemas for Enterprise Cloud Governance & Compliance Center.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ── Policy & Evaluation Schemas ───────────────────────────────────────────────


class GovernancePolicyItem(BaseModel):
  id: uuid.UUID
  name: str
  description: str | None = None
  category: str  # Security | FinOps | SRE | Kubernetes | Tagging | Operations
  severity: str  # LOW | MEDIUM | HIGH | CRITICAL
  provider: str  # AWS | Azure | GCP | Kubernetes | Multi-Cloud
  resource_type: str
  rule_identifier: str
  enabled: bool
  created_at: datetime
  updated_at: datetime

  model_config = {"from_attributes": True}


class GovernancePolicyCreatePayload(BaseModel):
  name: str = Field(..., min_length=3)
  description: str | None = None
  category: str = Field(default="Security")
  severity: str = Field(default="MEDIUM")
  provider: str = Field(default="Multi-Cloud")
  resource_type: str = Field(default="cloud_resource")
  rule_identifier: str | None = None
  enabled: bool = Field(default=True)


class GovernancePolicyUpdatePayload(BaseModel):
  name: str | None = None
  description: str | None = None
  category: str | None = None
  severity: str | None = None
  provider: str | None = None
  enabled: bool | None = None


class GovernancePolicyListResponse(BaseModel):
  policies: list[GovernancePolicyItem]
  total: int


class PolicyEvaluationItem(BaseModel):
  policy_name: str
  rule_identifier: str
  category: str
  severity: str
  provider: str
  resource_id: str
  resource_name: str
  resource_type: str
  region: str
  status: str  # PASS | FAIL | WARNING | NOT_APPLICABLE
  evidence: str
  recommended_action: str
  evaluated_at: str


class PolicyEvaluationListResponse(BaseModel):
  evaluations: list[PolicyEvaluationItem]
  total: int


# ── Framework & Violation Schemas ─────────────────────────────────────────────


class ComplianceFrameworkItem(BaseModel):
  framework: str  # CIS Controls | SOC 2 Type II | ISO/IEC 27001 | NIST SP 800-53 | PCI DSS
  version: str
  disclaimer: str = Field(
      default="Internal Control Mapping — Not a Certification"
  )
  total_controls: int
  passing_controls: int
  failing_controls: int
  coverage_percentage: float
  compliance_score: float
  status: str  # PASS | WARNING | FAIL


class ComplianceFrameworkListResponse(BaseModel):
  frameworks: list[ComplianceFrameworkItem]
  total: int


class GovernanceViolationItem(BaseModel):
  id: uuid.UUID
  policy_id: uuid.UUID
  policy_name: str
  category: str
  severity: str  # LOW | MEDIUM | HIGH | CRITICAL
  provider: str
  resource_id: str
  resource_name: str
  resource_type: str
  region: str
  status: str  # OPEN | ACKNOWLEDGED | IN_REMEDIATION | RESOLVED | WAIVED
  evidence: str
  recommended_action: str
  waived_by: uuid.UUID | None = None
  waiver_reason: str | None = None
  detected_at: datetime
  updated_at: datetime

  model_config = {"from_attributes": True}


class GovernanceViolationStatusPayload(BaseModel):
  status: str = Field(
      ..., description="OPEN | ACKNOWLEDGED | IN_REMEDIATION | RESOLVED | WAIVED"
  )
  reason: str | None = None


class GovernanceViolationListResponse(BaseModel):
  violations: list[GovernanceViolationItem]
  total_violations: int
  critical_violations: int


# ── Domain Governance & Remediation Schemas ───────────────────────────────────


class DomainGovernanceBreakdown(BaseModel):
  cost_governance: dict[str, Any]
  security_governance: dict[str, Any]
  sre_governance: dict[str, Any]
  kubernetes_governance: dict[str, Any]


class GovernanceRemediationItem(BaseModel):
  id: str
  violation_id: str
  resource: str
  category: str
  severity: str
  reason: str
  evidence: str
  recommended_action: str
  estimated_effort: str
  risk_reduction: str
  confidence: float
  workflow_automation_supported: bool = True


class GovernanceRemediationListResponse(BaseModel):
  remediations: list[GovernanceRemediationItem]
  total: int


# ── Audit & Trend Schemas ─────────────────────────────────────────────────────


class AuditEventItem(BaseModel):
  id: uuid.UUID
  action: str
  actor_user_id: uuid.UUID | None = None
  details: dict[str, Any]
  timestamp: datetime


class AuditTrailListResponse(BaseModel):
  audit_events: list[AuditEventItem]
  total: int


class GovernanceTrendPoint(BaseModel):
  day: str
  score: float
  violations: int


class GovernanceTrendResponse(BaseModel):
  horizon_days: int
  compliance_trend: list[GovernanceTrendPoint]
  resolved_violations_period: int
  new_violations_period: int
  policy_coverage_percentage: float


# ── Overview & AI Analysis Schemas ────────────────────────────────────────────


class GovernanceOverviewResponse(BaseModel):
  governance_score: float
  governance_rating: str  # EXCELLENT | GOOD | AT_RISK | CRITICAL
  compliance_score: float
  policies_evaluated_count: int
  passing_controls_count: int
  failing_controls_count: int
  open_violations: int
  critical_violations: int
  high_violations: int
  medium_violations: int
  low_violations: int
  data_source: str = Field(
      default="Local Governance Data — AWS/Azure/GCP/Kubernetes Fixtures"
  )
  scoring_methodology: str = Field(
      default=(
          "Weighted formula combining framework compliance score (70%),"
          " security policy coverage, cost-center tag alignment, SRE SLO"
          " governance, and Kubernetes pod security limits."
      )
  )


class GovernanceAnalyzeResponse(BaseModel):
  executive_summary: str
  critical_violations: list[str]
  framework_insights: list[str]
  remediation_recommendations: list[GovernanceRemediationItem]
  analyzed_at: str
  analysis_engine: str = Field(
      default="Local Governance Intelligence"
  )
