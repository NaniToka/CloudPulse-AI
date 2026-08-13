"""
CRUD Repository for Cloud Governance Policies, Violations, & Audit Events.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.governance import GovernancePolicy, GovernanceViolation
from app.services.audit_service import audit_service


async def seed_default_governance_policies_if_empty(
    db: AsyncSession, user_id: uuid.UUID | None = None
) -> None:
  """Seed default Cloud Governance Policies if table is empty."""
  count_stmt = select(func.count()).select_from(GovernancePolicy)
  res = await db.execute(count_stmt)
  if res.scalar_one() > 0:
    return

  now = datetime.now(UTC)
  default_policies = [
      (
          "Public Storage Access Disabled",
          "Ensure Cloud Storage Buckets (S3/Azure/GCS) do not allow unauthenticated public read/write access.",
          "Security",
          "CRITICAL",
          "Multi-Cloud",
          "storage_bucket",
          "GOV-SEC-001",
      ),
      (
          "Enforce Encryption at Rest",
          "Require AES-256 or KMS customer-managed key encryption for all cloud storage volumes and databases.",
          "Security",
          "HIGH",
          "Multi-Cloud",
          "cloud_resource",
          "GOV-SEC-002",
      ),
      (
          "Mandatory CostCenter & Owner Tags",
          "Enforce Environment, Owner, and CostCenter resource tags across all cloud assets for FinOps attribution.",
          "Tagging",
          "MEDIUM",
          "Multi-Cloud",
          "cloud_resource",
          "GOV-TAG-001",
      ),
      (
          "Approved Cloud Regions Control",
          "Restrict cloud resource provisioning to authorized corporate compliance regions (us-east-1, eastus, us-central1).",
          "FinOps",
          "HIGH",
          "Multi-Cloud",
          "cloud_resource",
          "GOV-REG-001",
      ),
      (
          "Automated Database Backup Retention",
          "Ensure production relational databases have daily automated snapshots and 30-day point-in-time recovery.",
          "Operations",
          "HIGH",
          "AWS",
          "rds_instance",
          "GOV-OPS-001",
      ),
      (
          "Kubernetes Container Resource Limits",
          "Enforce CPU and Memory limits on all Kubernetes pod deployments to prevent cluster OOM degradation.",
          "Kubernetes",
          "HIGH",
          "Kubernetes",
          "k8s_workload",
          "GOV-K8S-001",
      ),
      (
          "Non-Privileged Pod Container Execution",
          "Prohibit privileged container mode and root execution context on Kubernetes workloads.",
          "Kubernetes",
          "CRITICAL",
          "Kubernetes",
          "k8s_workload",
          "GOV-K8S-002",
      ),
      (
          "Infrastructure Telemetry Monitoring",
          "Ensure critical cloud virtual machines and containers have telemetry monitoring agents installed.",
          "Operations",
          "LOW",
          "Multi-Cloud",
          "cloud_resource",
          "GOV-OPS-002",
      ),
  ]

  for (
      name,
      desc,
      category,
      severity,
      provider,
      res_type,
      rule_id,
  ) in default_policies:
    pol = GovernancePolicy(
        id=uuid.uuid4(),
        name=name,
        description=desc,
        category=category,
        severity=severity,
        provider=provider,
        resource_type=res_type,
        rule_identifier=rule_id,
        enabled=True,
        user_id=user_id,
        created_at=now,
        updated_at=now,
    )
    db.add(pol)

  await db.flush()


async def get_policies(
    db: AsyncSession,
    *,
    category: str | None = None,
    provider: str | None = None,
    severity: str | None = None,
    user_id: uuid.UUID | None = None,
) -> list[GovernancePolicy]:
  """Fetch governance policies with optional filtering."""
  await seed_default_governance_policies_if_empty(db, user_id)
  stmt = select(GovernancePolicy).where(GovernancePolicy.enabled.is_(True))
  if category:
    stmt = stmt.where(GovernancePolicy.category == category)
  if provider:
    stmt = stmt.where(GovernancePolicy.provider == provider)
  if severity:
    stmt = stmt.where(GovernancePolicy.severity == severity.upper())

  stmt = stmt.order_by(
      GovernancePolicy.severity.asc(), GovernancePolicy.name.asc()
  )
  res = await db.execute(stmt)
  return list(res.scalars().all())


async def get_policy_by_id(
    db: AsyncSession, policy_id: uuid.UUID
) -> GovernancePolicy | None:
  """Fetch a single policy by UUID."""
  stmt = select(GovernancePolicy).where(GovernancePolicy.id == policy_id)
  res = await db.execute(stmt)
  return res.scalar_one_or_none()


async def create_policy(
    db: AsyncSession, user_id: uuid.UUID | None, data: dict[str, Any]
) -> GovernancePolicy:
  """Create a new governance policy."""
  pol = GovernancePolicy(
      id=uuid.uuid4(),
      name=data["name"],
      description=data.get("description"),
      category=data.get("category", "Security"),
      severity=data.get("severity", "MEDIUM").upper(),
      provider=data.get("provider", "Multi-Cloud"),
      resource_type=data.get("resource_type", "cloud_resource"),
      rule_identifier=data.get(
          "rule_identifier", f"GOV-CUSTOM-{uuid.uuid4().hex[:6].upper()}"
      ),
      enabled=data.get("enabled", True),
      user_id=user_id,
      created_at=datetime.now(UTC),
      updated_at=datetime.now(UTC),
  )
  db.add(pol)
  await db.flush()
  return pol


async def update_policy(
    db: AsyncSession, policy_id: uuid.UUID, data: dict[str, Any]
) -> GovernancePolicy | None:
  """Update an existing governance policy."""
  pol = await get_policy_by_id(db, policy_id)
  if not pol:
    return None

  if "name" in data and data["name"]:
    pol.name = data["name"]
  if "description" in data:
    pol.description = data["description"]
  if "category" in data and data["category"]:
    pol.category = data["category"]
  if "severity" in data and data["severity"]:
    pol.severity = data["severity"].upper()
  if "provider" in data and data["provider"]:
    pol.provider = data["provider"]
  if "enabled" in data and data["enabled"] is not None:
    pol.enabled = data["enabled"]

  pol.updated_at = datetime.now(UTC)
  db.add(pol)
  await db.flush()
  return pol


# ── Violation CRUD & Lifecycle Operations ────────────────────────────────────


async def get_violations(
    db: AsyncSession,
    *,
    status: str | None = None,
    severity: str | None = None,
    provider: str | None = None,
    category: str | None = None,
) -> list[GovernanceViolation]:
  """Fetch policy violations with optional status/severity filtering."""
  stmt = select(GovernanceViolation)
  if status:
    stmt = stmt.where(GovernanceViolation.status == status.upper())
  if severity:
    stmt = stmt.where(GovernanceViolation.severity == severity.upper())
  if provider:
    stmt = stmt.where(GovernanceViolation.provider == provider)
  if category:
    stmt = stmt.where(GovernanceViolation.category == category)

  stmt = stmt.order_by(GovernanceViolation.detected_at.desc())
  res = await db.execute(stmt)
  return list(res.scalars().all())


async def get_violation_by_id(
    db: AsyncSession, violation_id: uuid.UUID
) -> GovernanceViolation | None:
  """Fetch a single violation by UUID."""
  stmt = select(GovernanceViolation).where(
      GovernanceViolation.id == violation_id
  )
  res = await db.execute(stmt)
  return res.scalar_one_or_none()


async def update_violation_status(
    db: AsyncSession,
    violation_id: uuid.UUID,
    new_status: str,
    user_id: uuid.UUID | None,
    organization_id: uuid.UUID | None,
    reason: str | None = None,
) -> GovernanceViolation | None:
  """
  Update violation lifecycle state (OPEN -> ACKNOWLEDGED -> IN_REMEDIATION -> RESOLVED / WAIVED)
  and record security audit trail event.
  """
  violation = await get_violation_by_id(db, violation_id)
  if not violation:
    return None

  prev_state = violation.status
  violation.status = new_status.upper()
  violation.updated_at = datetime.now(UTC)

  if new_status.upper() == "WAIVED":
    violation.waived_by = user_id
    violation.waiver_reason = reason or "Waiver approved by security admin."

  db.add(violation)
  await db.flush()

  # Record audit event using existing audit_service
  if organization_id:
    await audit_service.log_event(
        db,
        organization_id=organization_id,
        user_id=user_id,
        action="GOVERNANCE_VIOLATION_STATUS_CHANGE",
        details={
            "violation_id": str(violation_id),
            "resource_id": violation.resource_id,
            "previous_state": prev_state,
            "new_state": new_status.upper(),
            "reason": reason,
        },
    )

  return violation
