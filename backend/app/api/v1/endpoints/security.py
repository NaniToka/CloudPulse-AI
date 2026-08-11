"""
AI Security & Cloud Compliance Center REST API Endpoints.
"""

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.security import (
    ComplianceReportResponse,
    RiskScoreResponse,
    SecurityFindingResponse,
    SecurityListResponse,
    SecurityOverviewResponse,
    SecurityRecommendation,
    SecurityScanPayload,
    SecurityScanResponse,
    SecurityStatusUpdatePayload,
)
from app.services.security_service import SecurityService, security_service

log = structlog.get_logger(__name__)

router = APIRouter()


def get_security_service() -> SecurityService:
    return security_service


async def _seed_initial_security_scans_if_empty(db: AsyncSession, service: SecurityService) -> None:
    items, total, _ = await service.list_findings(db, size=1)
    if total == 0:
        log.info("seeding_initial_security_findings")
        await service.run_security_scan(db, SecurityScanPayload(provider="ALL"))


@router.post(
    "/scan",
    response_model=SecurityScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger cloud security scan",
)
async def trigger_security_scan(
    payload: SecurityScanPayload,
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Executes automated CSPM cloud security scan and AI threat analysis."""
    return await service.run_security_scan(db, payload)


@router.get(
    "/overview",
    response_model=SecurityOverviewResponse,
    summary="Get security posture overview",
)
async def get_security_overview(
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Retrieve posture score, finding statistics, compliance summary, and threat vectors."""
    await _seed_initial_security_scans_if_empty(db, service)
    return await service.get_overview(db)


@router.get("/findings", response_model=SecurityListResponse, summary="List security findings")
async def list_security_findings(
    severity: str | None = Query(
        None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)"
    ),
    category: str | None = Query(
        None, description="Filter by category (IAM, Network, Storage, Database, Secrets, Compute, Kubernetes)"
    ),
    provider: str | None = Query(None, description="Filter by provider (AWS, GCP, Azure, Kubernetes)"),
    framework: str | None = Query(None, description="Filter by compliance framework"),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by status (OPEN, INVESTIGATING, MITIGATED, RESOLVED, ACCEPTED_RISK)"
    ),
    search: str | None = Query(None, description="Search in scan_name, resource, or description"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Retrieve paginated list of cloud security findings."""
    await _seed_initial_security_scans_if_empty(db, service)
    items, total, pages = await service.list_findings(
        db,
        severity=severity,
        category=category,
        provider=provider,
        framework=framework,
        status=status_filter,
        search=search,
        page=page,
        size=size,
    )
    return SecurityListResponse(
        items=[SecurityFindingResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/findings/{finding_id}",
    response_model=SecurityFindingResponse,
    summary="Get security finding details",
)
async def get_security_finding_by_id(
    finding_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Retrieve complete evidence, risk score, and AI threat analysis for a single finding."""
    finding = await service.get_finding_by_id(db, finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security finding with ID {finding_id} not found.",
        )
    return SecurityFindingResponse.model_validate(finding)


@router.patch(
    "/findings/{finding_id}/status",
    response_model=SecurityFindingResponse,
    summary="Update security finding status",
)
async def update_security_finding_status(
    finding_id: uuid.UUID,
    payload: SecurityStatusUpdatePayload,
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Update status of a security finding (OPEN, INVESTIGATING, MITIGATED, RESOLVED, ACCEPTED_RISK)."""
    updated = await service.update_finding_status(db, finding_id, payload.status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security finding with ID {finding_id} not found.",
        )
    return SecurityFindingResponse.model_validate(updated)


@router.get(
    "/recommendations",
    response_model=list[SecurityRecommendation],
    summary="Get security recommendations",
)
async def get_security_recommendations(
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Retrieve prioritized actionable security recommendations."""
    await _seed_initial_security_scans_if_empty(db, service)
    return await service.get_recommendations(db)


@router.get(
    "/compliance",
    response_model=list[ComplianceReportResponse],
    summary="Get compliance scorecards",
)
async def get_compliance_scorecards(
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Retrieve compliance framework scorecards (CIS, ISO 27001, SOC 2, NIST CSF, PCI DSS, HIPAA, GDPR)."""
    reports = await service.get_compliance_reports(db)
    return [ComplianceReportResponse.model_validate(r) for r in reports]


@router.get(
    "/risk-score", response_model=RiskScoreResponse, summary="Get security posture & risk metrics"
)
async def get_risk_score_summary(
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Compute overall security score, risk score (0-10), and severity distribution."""
    await _seed_initial_security_scans_if_empty(db, service)
    return await service.get_risk_score(db)


@router.get("/report", summary="Get executive compliance & security report summary")
async def get_security_executive_report(
    db: AsyncSession = Depends(get_db),
    service: SecurityService = Depends(get_security_service),
):
    """Generate executive cloud security & compliance posture summary report."""
    await _seed_initial_security_scans_if_empty(db, service)
    risk_summary = await service.get_risk_score(db)
    reports = await service.get_compliance_reports(db)

    return {
        "title": "CloudPulse AI Executive Security & Compliance Report",
        "overall_security_score": risk_summary["overall_security_score"],
        "risk_level": risk_summary.get("risk_level", "High"),
        "compliance_summary": [
            {
                "framework": r.framework,
                "score": r.overall_score,
                "passed": r.passed_controls,
                "failed": r.failed_controls,
            }
            for r in reports
        ],
        "top_recommendations": [
            "Enable S3 Block Public Access on production backup buckets.",
            "Enforce MFA for all Root and IAM Administrator accounts.",
            "Remove 0.0.0.0/0 SSH/RDP ingress rules from security groups.",
            "Migrate plaintext database passwords in ConfigMaps to Vault/Secrets Manager.",
        ],
    }
