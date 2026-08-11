"""
Service Layer for AI Security & Cloud Compliance Center.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_security import crud_security
from app.models.security import ComplianceReport, SecurityScan
from app.schemas.security import (
    ComplianceReportResponse,
    SecurityOverviewResponse,
    SecurityRecommendation,
    SecurityScanPayload,
    SecurityScanResponse,
)
from app.services.security_ai_service import analyze_security_finding
from app.services.security_detection_engine import security_detection_engine
from app.services.security_risk_engine import security_risk_engine

log = structlog.get_logger(__name__)


class SecurityService:
    """Security Service handling CSPM scans, compliance reports, and threat analysis."""

    def __init__(self, crud_repo=crud_security) -> None:
        self.crud = crud_repo

    async def list_findings(
        self,
        db: AsyncSession,
        *,
        severity: str | None = None,
        category: str | None = None,
        provider: str | None = None,
        framework: str | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[SecurityScan], int, int]:
        return await self.crud.get_filtered_findings(
            db,
            severity=severity,
            category=category,
            provider=provider,
            framework=framework,
            status=status,
            search=search,
            page=page,
            size=size,
        )

    async def get_finding_by_id(self, db: AsyncSession, finding_id: uuid.UUID) -> SecurityScan | None:
        return await self.crud.get_finding_by_id(db, finding_id)

    async def update_finding_status(
        self, db: AsyncSession, finding_id: uuid.UUID, new_status: str
    ) -> SecurityScan | None:
        return await self.crud.update_status(db, finding_id, new_status)

    async def get_compliance_reports(self, db: AsyncSession) -> list[ComplianceReport]:
        """Retrieve or seed compliance framework scorecards."""
        reports = await self.crud.get_compliance_reports(db)
        if not reports:
            reports = await self._seed_compliance_reports(db)
        return reports

    async def get_risk_score(self, db: AsyncSession) -> dict[str, Any]:
        """Compute aggregate cloud security risk score metrics."""
        return await self.crud.get_risk_score_summary(db)

    async def get_recommendations(self, db: AsyncSession) -> list[SecurityRecommendation]:
        """Generate prioritized security recommendations."""
        findings, _, _ = await self.crud.get_filtered_findings(db, size=20)

        recommendations: list[SecurityRecommendation] = []
        for idx, f in enumerate(findings):
            if f.status.upper() in ("RESOLVED", "ACCEPTED_RISK"):
                continue
            recommendations.append(
                SecurityRecommendation(
                    id=str(f.id),
                    title=f.scan_name,
                    severity=f.severity,
                    category=f.category,
                    resource=f.resource,
                    action=f.recommendation,
                    fix_time_estimate="15 mins" if f.severity.upper() == "CRITICAL" else "30 mins",
                    compliance_framework=f.compliance_framework,
                )
            )

        return recommendations[:10]

    async def get_overview(self, db: AsyncSession) -> SecurityOverviewResponse:
        """Fetch comprehensive posture overview."""
        risk_summary = await self.get_risk_score(db)
        reports = await self.get_compliance_reports(db)
        recs = await self.get_recommendations(db)

        findings, total_open, _ = await self.crud.get_filtered_findings(db, status="OPEN", size=100)

        threat_vectors = [
            {
                "name": "Public S3 / Blob Storage Exposure",
                "count": sum(1 for f in findings if f.category.upper() == "STORAGE"),
                "risk": "Critical",
            },
            {
                "name": "Excessive IAM Role / ServiceAccount Privileges",
                "count": sum(1 for f in findings if f.category.upper() == "IAM"),
                "risk": "High",
            },
            {
                "name": "Open Ingress Ports (SSH/RDP/K8s API)",
                "count": sum(1 for f in findings if f.category.upper() == "NETWORK"),
                "risk": "Critical",
            },
            {
                "name": "Unencrypted Database Instances & Backups",
                "count": sum(1 for f in findings if f.category.upper() == "DATABASE"),
                "risk": "High",
            },
        ]

        return SecurityOverviewResponse(
            posture_score=risk_summary["overall_security_score"],
            overall_risk_score=risk_summary["overall_risk_score"],
            risk_level=risk_summary.get("risk_level", "Medium"),
            open_findings_count=total_open,
            critical_findings_count=risk_summary["critical_findings_count"],
            high_findings_count=risk_summary["high_findings_count"],
            medium_findings_count=risk_summary.get("medium_findings_count", 0),
            low_findings_count=risk_summary.get("low_findings_count", 0),
            resources_at_risk_count=risk_summary["resources_at_risk_count"],
            compliance_scorecards=[ComplianceReportResponse.model_validate(r) for r in reports],
            top_recommendations=recs,
            threat_vectors=threat_vectors,
        )

    async def run_security_scan(
        self, db: AsyncSession, payload: SecurityScanPayload
    ) -> SecurityScanResponse:
        """Executes automated security scan across simulated cloud infrastructure."""
        provider = payload.provider or "AWS"
        raw_scans = security_detection_engine.generate_findings(provider_filter=provider)

        now = datetime.now(UTC)
        crit_cnt = 0
        high_cnt = 0
        med_cnt = 0
        low_cnt = 0

        for s in raw_scans:
            ai_analysis = await analyze_security_finding(s)

            risk_eval = security_risk_engine.calculate_finding_risk(
                severity=s["severity"],
                category=s["category"],
                resource_type=s.get("resource_type", "cloud_resource"),
                is_publicly_exposed=("0.0.0.0" in str(s) or "public" in str(s).lower()),
                has_admin_privileges=("admin" in str(s).lower() or "privileged" in str(s).lower()),
                confidence=s.get("confidence", 0.92),
            )

            scan_obj = SecurityScan(
                id=uuid.uuid4(),
                scan_name=s["scan_name"],
                provider=s["provider"],
                region=s["region"],
                resource=s["resource"],
                resource_type=s.get("resource_type", "s3_bucket"),
                severity=s["severity"],
                category=s["category"],
                compliance_framework=s["compliance_framework"],
                description=s["description"],
                recommendation=s["recommendation"],
                risk_score=risk_eval["risk_score"],
                confidence=risk_eval["confidence"],
                evidence=s.get("evidence", []),
                ai_analysis=ai_analysis,
                status=s.get("status", "OPEN"),
                first_detected_at=s.get("first_detected_at", now),
                last_detected_at=s.get("last_detected_at", now),
                created_at=now,
                updated_at=now,
            )
            db.add(scan_obj)

            sev = s["severity"].upper()
            if sev == "CRITICAL":
                crit_cnt += 1
            elif sev == "HIGH":
                high_cnt += 1
            elif sev == "MEDIUM":
                med_cnt += 1
            else:
                low_cnt += 1

        await db.flush()

        summary = await self.get_risk_score(db)

        return SecurityScanResponse(
            total_findings=len(raw_scans),
            critical_findings=crit_cnt,
            high_findings=high_cnt,
            medium_findings=med_cnt,
            low_findings=low_cnt,
            scanned_resources=len(raw_scans) * 3,
            overall_security_score=summary["overall_security_score"],
            message=f"Cloud security scan completed successfully across {provider} infrastructure.",
        )

    async def _seed_compliance_reports(self, db: AsyncSession) -> list[ComplianceReport]:
        """Seed default compliance framework scorecards."""
        now = datetime.now(UTC)
        frameworks = [
            {"framework": "CIS Benchmarks", "score": 92.5, "passed": 37, "failed": 3, "total": 40},
            {"framework": "ISO 27001", "score": 88.0, "passed": 44, "failed": 6, "total": 50},
            {"framework": "SOC 2", "score": 90.0, "passed": 36, "failed": 4, "total": 40},
            {"framework": "NIST CSF", "score": 85.0, "passed": 51, "failed": 9, "total": 60},
            {"framework": "PCI DSS", "score": 94.0, "passed": 47, "failed": 3, "total": 50},
            {"framework": "HIPAA", "score": 89.0, "passed": 31, "failed": 4, "total": 35},
            {"framework": "GDPR", "score": 91.0, "passed": 27, "failed": 3, "total": 30},
        ]

        created = []
        for f in frameworks:
            cr = ComplianceReport(
                id=uuid.uuid4(),
                framework=f["framework"],
                overall_score=f["score"],
                passed_controls=f["passed"],
                failed_controls=f["failed"],
                total_controls=f["total"],
                category_scores={"IAM": 92.0, "Network": 85.0, "Storage": 88.0, "Database": 90.0},
                created_at=now,
            )
            db.add(cr)
            created.append(cr)

        await db.flush()
        return created


security_service = SecurityService()
