"""
Service Layer for AI Security & Cloud Compliance Center.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.crud.crud_security import crud_security
from app.models.security import SecurityScan, ComplianceReport
from app.schemas.security import SecurityScanPayload, SecurityScanResponse
from app.services.security_scanners import run_cloud_security_scanners
from app.services.security_ai_service import analyze_security_finding

log = structlog.get_logger(__name__)


class SecurityService:
    """Security Service handling CSPM scans, compliance reports, and threat analysis."""

    def __init__(self, crud_repo=crud_security) -> None:
        self.crud = crud_repo

    async def list_findings(
        self,
        db: AsyncSession,
        *,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        provider: Optional[str] = None,
        framework: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> Tuple[List[SecurityScan], int, int]:
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

    async def get_compliance_reports(self, db: AsyncSession) -> List[ComplianceReport]:
        """Retrieve or seed compliance framework scorecards."""
        reports = await self.crud.get_compliance_reports(db)
        if not reports:
            reports = await self._seed_compliance_reports(db)
        return reports

    async def get_risk_score(self, db: AsyncSession) -> Dict[str, Any]:
        """Compute aggregate cloud security risk score metrics."""
        return await self.crud.get_risk_score_summary(db)

    async def run_security_scan(self, db: AsyncSession, payload: SecurityScanPayload) -> SecurityScanResponse:
        """Executes automated security scan across simulated cloud infrastructure."""
        provider = payload.provider or "AWS"
        raw_scans = run_cloud_security_scanners(provider)

        now = datetime.now(timezone.utc)
        crit_cnt = 0
        high_cnt = 0
        med_cnt = 0
        low_cnt = 0

        for s in raw_scans:
            ai_analysis = await analyze_security_finding(s)

            scan_obj = SecurityScan(
                id=uuid.uuid4(),
                scan_name=s["scan_name"],
                provider=s["provider"],
                region=s["region"],
                resource=s["resource"],
                severity=s["severity"],
                category=s["category"],
                compliance_framework=s["compliance_framework"],
                description=s["description"],
                recommendation=s["recommendation"],
                ai_analysis=ai_analysis,
                status="Open",
                created_at=now,
                updated_at=now,
            )
            db.add(scan_obj)

            sev = s["severity"]
            if sev == "Critical":
                crit_cnt += 1
            elif sev == "High":
                high_cnt += 1
            elif sev == "Medium":
                med_cnt += 1
            else:
                low_cnt += 1

        await db.commit()

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

    async def _seed_compliance_reports(self, db: AsyncSession) -> List[ComplianceReport]:
        """Seed default compliance framework scorecards."""
        now = datetime.now(timezone.utc)
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

        await db.commit()
        return created


security_service = SecurityService()
