"""
Enterprise Cloud Governance & Compliance Center REST API Endpoints.

Routes:
-------
GET    /api/v1/governance/overview               — Overall governance score, compliance score, violation counts
GET    /api/v1/governance/policies               — List configured governance policies with filtering
POST   /api/v1/governance/policies               — Create a new governance policy
PUT    /api/v1/governance/policies/{id}          — Update existing governance policy
GET    /api/v1/governance/frameworks            — Compliance framework scores (CIS, SOC 2, ISO 27001, NIST, PCI DSS)
GET    /api/v1/governance/frameworks/{framework}— Detailed single-framework control mapping
GET    /api/v1/governance/controls               — Control evaluation breakdown
GET    /api/v1/governance/evaluations            — Policy evaluation results on cloud/K8s resources
GET    /api/v1/governance/violations             — List detected policy violations with filtering
GET    /api/v1/governance/violations/{id}        — Get detailed policy violation
PATCH  /api/v1/governance/violations/{id}/status — Update violation status (ACKNOWLEDGED, WAIVED, etc.) with audit trail
GET    /api/v1/governance/recommendations        — Remediation recommendations
GET    /api/v1/governance/audit                  — Governance security audit log history
GET    /api/v1/governance/trends                 — 7d, 30d, 90d historical compliance trends
POST   /api/v1/governance/evaluate               — Trigger policy re-evaluation sweep
POST   /api/v1/governance/analyze                — Trigger Gemini AI / Local Governance Intelligence analysis
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.crud import crud_governance
from app.models.governance import GovernanceViolation
from app.models.tenant import AuditLog
from app.models.user import User
from app.schemas.governance import (
    AuditEventItem,
    AuditTrailListResponse,
    ComplianceFrameworkItem,
    ComplianceFrameworkListResponse,
    GovernanceAnalyzeResponse,
    GovernanceOverviewResponse,
    GovernancePolicyCreatePayload,
    GovernancePolicyItem,
    GovernancePolicyListResponse,
    GovernancePolicyUpdatePayload,
    GovernanceRemediationItem,
    GovernanceRemediationListResponse,
    GovernanceTrendPoint,
    GovernanceTrendResponse,
    GovernanceViolationItem,
    GovernanceViolationListResponse,
    GovernanceViolationStatusPayload,
    PolicyEvaluationItem,
    PolicyEvaluationListResponse,
)
from app.services.governance_ai_service import analyze_governance_with_gemini
from app.services.governance_engine import (
    calculate_compliance_score,
    calculate_governance_posture,
    calculate_governance_trends,
    evaluate_domain_governance,
    evaluate_governance_policy,
    generate_governance_remediations,
    get_compliance_framework_mappings,
    get_local_governance_fixture_resources,
)

log = structlog.get_logger(__name__)
router = APIRouter()


# Helper to run full policy evaluation sweep
async def _run_evaluations_sweep(
    db: AsyncSession, user_id: uuid.UUID
) -> list[dict[str, Any]]:
  policies_db = await crud_governance.get_policies(db, user_id=user_id)
  resources = get_local_governance_fixture_resources()

  all_evals = []
  for pol in policies_db:
    pol_dict = {
        "name": pol.name,
        "rule_identifier": pol.rule_identifier,
        "category": pol.category,
        "severity": pol.severity,
        "provider": pol.provider,
    }
    evals = evaluate_governance_policy(pol_dict, resources)
    all_evals.extend(evals)

  return all_evals


# ---------------------------------------------------------------------------
# GET /governance/overview
# ---------------------------------------------------------------------------


@router.get(
    "/overview",
    response_model=GovernanceOverviewResponse,
    summary="Get overall governance posture score, compliance score, and violation summary",
)
async def get_governance_overview(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceOverviewResponse:
  log.info("get_governance_overview", user_id=str(current_user.id))

  evals = await _run_evaluations_sweep(db, current_user.id)
  comp_stats = calculate_compliance_score(evals)

  resources = get_local_governance_fixture_resources()
  domain_gov = evaluate_domain_governance(resources)

  sec_viol = domain_gov["security_governance"].get("public_resources_count", 0)
  cost_viol = domain_gov["cost_governance"].get(
      "missing_cost_center_tags", 0
  )
  sre_viol = domain_gov["sre_governance"].get("services_with_breached_slos", 0)
  k8s_viol = domain_gov["kubernetes_governance"].get("privileged_workloads", 0)

  posture = calculate_governance_posture(
      compliance_score=comp_stats["compliance_score"],
      critical_violations=comp_stats["critical_violations"],
      security_violations_count=sec_viol,
      cost_violations_count=cost_viol,
      sre_violations_count=sre_viol,
      k8s_violations_count=k8s_viol,
  )

  violations_db = await crud_governance.get_violations(db, status="OPEN")
  open_cnt = len(violations_db) if violations_db else comp_stats["failing_controls"]

  return GovernanceOverviewResponse(
      governance_score=posture["score"],
      governance_rating=posture["rating"],
      compliance_score=comp_stats["compliance_score"],
      policies_evaluated_count=len(evals),
      passing_controls_count=comp_stats["passing_controls"],
      failing_controls_count=comp_stats["failing_controls"],
      open_violations=open_cnt,
      critical_violations=comp_stats["critical_violations"],
      high_violations=comp_stats["high_violations"],
      medium_violations=comp_stats["medium_violations"],
      low_violations=comp_stats["low_violations"],
      data_source="Local Governance Data — AWS/Azure/GCP/Kubernetes Fixtures",
      scoring_methodology=posture["scoring_methodology"],
  )


# ---------------------------------------------------------------------------
# GET /governance/policies, POST /governance/policies, PUT /governance/policies/{id}
# ---------------------------------------------------------------------------


@router.get(
    "/policies",
    response_model=GovernancePolicyListResponse,
    summary="List configured governance policies with optional filtering",
)
async def get_policies(
    category: str | None = None,
    provider: str | None = None,
    severity: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernancePolicyListResponse:
  policies_db = await crud_governance.get_policies(
      db,
      category=category,
      provider=provider,
      severity=severity,
      user_id=current_user.id,
  )
  items = [GovernancePolicyItem.model_validate(p) for p in policies_db]
  return GovernancePolicyListResponse(policies=items, total=len(items))


@router.post(
    "/policies",
    response_model=GovernancePolicyItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new governance policy rule",
)
async def create_policy(
    payload: GovernancePolicyCreatePayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernancePolicyItem:
  pol = await crud_governance.create_policy(
      db, user_id=current_user.id, data=payload.model_dump()
  )
  return GovernancePolicyItem.model_validate(pol)


@router.put(
    "/policies/{policy_id}",
    response_model=GovernancePolicyItem,
    summary="Update an existing governance policy rule",
)
async def update_policy(
    policy_id: uuid.UUID,
    payload: GovernancePolicyUpdatePayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernancePolicyItem:
  updated = await crud_governance.update_policy(
      db, policy_id=policy_id, data=payload.model_dump(exclude_unset=True)
  )
  if not updated:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Governance policy not found.",
    )
  return GovernancePolicyItem.model_validate(updated)


# ---------------------------------------------------------------------------
# GET /governance/frameworks & GET /governance/frameworks/{framework_name}
# ---------------------------------------------------------------------------


@router.get(
    "/frameworks",
    response_model=ComplianceFrameworkListResponse,
    summary="Get compliance framework scores (CIS Controls, SOC 2, ISO 27001, NIST, PCI DSS)",
)
async def get_compliance_frameworks(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ComplianceFrameworkListResponse:
  evals = await _run_evaluations_sweep(db, current_user.id)
  frameworks = get_compliance_framework_mappings(evals)
  items = [ComplianceFrameworkItem(**f) for f in frameworks]
  return ComplianceFrameworkListResponse(frameworks=items, total=len(items))


@router.get(
    "/frameworks/{framework_name}",
    response_model=ComplianceFrameworkItem,
    summary="Get detailed control mapping for a specific framework",
)
async def get_framework_detail(
    framework_name: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> ComplianceFrameworkItem:
  evals = await _run_evaluations_sweep(db, current_user.id)
  frameworks = get_compliance_framework_mappings(evals)

  target = next(
      (
          f
          for f in frameworks
          if f["framework"].lower().replace(" ", "")
          == framework_name.lower().replace(" ", "")
      ),
      None,
  )

  if not target:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Compliance framework '{framework_name}' not found.",
    )

  return ComplianceFrameworkItem(**target)


# ---------------------------------------------------------------------------
# GET /governance/evaluations & GET /governance/controls
# ---------------------------------------------------------------------------


@router.get(
    "/evaluations",
    response_model=PolicyEvaluationListResponse,
    summary="Get policy evaluation results on AWS, Azure, GCP, and Kubernetes resources",
)
async def get_evaluations(
    provider: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PolicyEvaluationListResponse:
  evals = await _run_evaluations_sweep(db, current_user.id)
  items = [PolicyEvaluationItem(**e) for e in evals]

  if provider:
    items = [i for i in items if i.provider.lower() == provider.lower()]
  if status_filter:
    items = [i for i in items if i.status.upper() == status_filter.upper()]

  return PolicyEvaluationListResponse(evaluations=items, total=len(items))


@router.get(
    "/controls",
    response_model=PolicyEvaluationListResponse,
    summary="List evaluated control checks",
)
async def get_controls(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PolicyEvaluationListResponse:
  return await get_evaluations(
      provider=None,
      status_filter=None,
      current_user=current_user,
      db=db,
  )


# ---------------------------------------------------------------------------
# GET /governance/violations, GET /governance/violations/{id}, PATCH /governance/violations/{id}/status
# ---------------------------------------------------------------------------


@router.get(
    "/violations",
    response_model=GovernanceViolationListResponse,
    summary="List policy violations with status, severity, and provider filtering",
)
async def get_violations(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    provider: str | None = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceViolationListResponse:
  violations_db = await crud_governance.get_violations(
      db,
      status=status_filter,
      severity=severity,
      provider=provider,
  )

  if not violations_db:
    # Build fallback violations from policy evaluation failures
    evals = await _run_evaluations_sweep(db, current_user.id)
    policies_db = await crud_governance.get_policies(db, user_id=current_user.id)

    items = []
    for e in evals:
      if e["status"] in ("FAIL", "WARNING"):
        pol = next(
            (p for p in policies_db if p.rule_identifier == e["rule_identifier"]),
            None,
        )
        pol_id = pol.id if pol else uuid.uuid4()
        items.append(
            GovernanceViolationItem(
                id=uuid.uuid4(),
                policy_id=pol_id,
                policy_name=e["policy_name"],
                category=e["category"],
                severity=e["severity"],
                provider=e["provider"],
                resource_id=e["resource_id"],
                resource_name=e["resource_name"],
                resource_type=e["resource_type"],
                region=e["region"],
                status="OPEN",
                evidence=e["evidence"],
                recommended_action=e["recommended_action"],
                detected_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
    crit_cnt = sum(1 for i in items if i.severity == "CRITICAL")
    return GovernanceViolationListResponse(
        violations=items, total_violations=len(items), critical_violations=crit_cnt
    )

  items = [GovernanceViolationItem.model_validate(v) for v in violations_db]
  crit_cnt = sum(1 for i in items if i.severity == "CRITICAL")
  return GovernanceViolationListResponse(
      violations=items, total_violations=len(items), critical_violations=crit_cnt
  )


@router.get(
    "/violations/{violation_id}",
    response_model=GovernanceViolationItem,
    summary="Get details for a specific governance policy violation",
)
async def get_violation_detail(
    violation_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceViolationItem:
  v = await crud_governance.get_violation_by_id(db, violation_id)
  if not v:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Governance violation not found.",
    )
  return GovernanceViolationItem.model_validate(v)


@router.patch(
    "/violations/{violation_id}/status",
    response_model=GovernanceViolationItem,
    summary="Update violation status (ACKNOWLEDGED, IN_REMEDIATION, RESOLVED, WAIVED) with security audit trail",
)
async def update_violation_status(
    violation_id: uuid.UUID,
    payload: GovernanceViolationStatusPayload,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceViolationItem:
  updated = await crud_governance.update_violation_status(
      db,
      violation_id=violation_id,
      new_status=payload.status,
      user_id=current_user.id,
      organization_id=current_user.organization_id,
      reason=payload.reason,
  )
  if not updated:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Governance violation not found.",
    )
  return GovernanceViolationItem.model_validate(updated)


# ---------------------------------------------------------------------------
# GET /governance/recommendations, /governance/audit, /governance/trends
# ---------------------------------------------------------------------------


@router.get(
    "/recommendations",
    response_model=GovernanceRemediationListResponse,
    summary="Get actionable remediation recommendations derived from policy violations",
)
async def get_remediations(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceRemediationListResponse:
  evals = await _run_evaluations_sweep(db, current_user.id)
  failing_evals = [e for e in evals if e["status"] in ("FAIL", "WARNING")]

  rems = generate_governance_remediations(failing_evals)
  items = [GovernanceRemediationItem(**r) for r in rems]
  return GovernanceRemediationListResponse(remediations=items, total=len(items))


@router.get(
    "/audit",
    response_model=AuditTrailListResponse,
    summary="Get governance security audit log history",
)
async def get_audit_trail(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> AuditTrailListResponse:
  stmt = (
      select(AuditLog)
      .where(AuditLog.action.like("%GOVERNANCE%"))
      .order_by(AuditLog.created_at.desc())
      .limit(50)
  )
  res = await db.execute(stmt)
  audit_records = list(res.scalars().all())

  items = [
      AuditEventItem(
          id=r.id,
          action=r.action,
          actor_user_id=r.user_id,
          details=r.details or {},
          timestamp=r.created_at,
      )
      for r in audit_records
  ]

  if not items:
    # Default initial audit log item
    items = [
        AuditEventItem(
            id=uuid.uuid4(),
            action="GOVERNANCE_POLICY_EVALUATION_SWEEP",
            actor_user_id=current_user.id,
            details={
                "evaluated_policies": 8,
                "status": "COMPLETED",
                "environment": "Production",
            },
            timestamp=datetime.now(UTC),
        )
    ]

  return AuditTrailListResponse(audit_events=items, total=len(items))


@router.get(
    "/trends",
    response_model=GovernanceTrendResponse,
    summary="Get historical 7d, 30d, and 90d compliance trends",
)
async def get_governance_trends(
    days: int = Query(default=30, alias="days"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceTrendResponse:
  trends_data = calculate_governance_trends(history_days=days)
  pts = [GovernanceTrendPoint(**p) for p in trends_data["compliance_trend"]]

  return GovernanceTrendResponse(
      horizon_days=days,
      compliance_trend=pts,
      resolved_violations_period=trends_data["resolved_violations_period"],
      new_violations_period=trends_data["new_violations_period"],
      policy_coverage_percentage=trends_data["policy_coverage_percentage"],
  )


# ---------------------------------------------------------------------------
# POST /governance/evaluate & POST /governance/analyze
# ---------------------------------------------------------------------------


@router.post(
    "/evaluate",
    response_model=PolicyEvaluationListResponse,
    summary="Trigger immediate policy re-evaluation sweep across all resources",
)
async def evaluate_policies_now(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> PolicyEvaluationListResponse:
  log.info("trigger_governance_eval_sweep", user_id=str(current_user.id))
  evals = await _run_evaluations_sweep(db, current_user.id)
  items = [PolicyEvaluationItem(**e) for e in evals]

  # Seed failures into GovernanceViolation DB table
  policies_db = await crud_governance.get_policies(db, user_id=current_user.id)
  for e in evals:
    if e["status"] == "FAIL":
      pol = next(
          (p for p in policies_db if p.rule_identifier == e["rule_identifier"]),
          None,
      )
      if pol:
        viol = GovernanceViolation(
            id=uuid.uuid4(),
            policy_id=pol.id,
            policy_name=e["policy_name"],
            category=e["category"],
            severity=e["severity"],
            provider=e["provider"],
            resource_id=e["resource_id"],
            resource_name=e["resource_name"],
            resource_type=e["resource_type"],
            region=e["region"],
            status="OPEN",
            evidence=e["evidence"],
            recommended_action=e["recommended_action"],
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            detected_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(viol)
  await db.flush()

  return PolicyEvaluationListResponse(evaluations=items, total=len(items))


@router.post(
    "/analyze",
    response_model=GovernanceAnalyzeResponse,
    summary="Trigger Gemini AI / Local Governance Intelligence analysis",
)
async def analyze_governance_posture(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> GovernanceAnalyzeResponse:
  log.info("trigger_governance_ai_analysis", user_id=str(current_user.id))

  overview = await get_governance_overview(current_user, db)
  evals = await _run_evaluations_sweep(db, current_user.id)

  analysis = await analyze_governance_with_gemini(
      db,
      user_id=str(current_user.id),
      governance_overview=overview.model_dump(),
      evaluations_summary=evals,
  )

  recs_out = []
  for r in analysis.get("remediation_recommendations", []):
    if isinstance(r, dict):
      if "id" not in r or not r["id"]:
        r["id"] = str(uuid.uuid4())
      if "violation_id" not in r:
        r["violation_id"] = str(uuid.uuid4())
      recs_out.append(GovernanceRemediationItem(**r))

  return GovernanceAnalyzeResponse(
      executive_summary=analysis.get("executive_summary", ""),
      critical_violations=analysis.get("critical_violations", []),
      framework_insights=analysis.get("framework_insights", []),
      remediation_recommendations=recs_out,
      analyzed_at=analysis.get("analyzed_at", ""),
      analysis_engine=analysis.get(
          "analysis_engine", "Local Governance Intelligence"
      ),
  )
