"""
SecurityScan and ComplianceReport SQLAlchemy models for AI Security & Compliance Center.
"""

from sqlalchemy import JSON, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class SecurityScan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "security_scans"

    scan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="AWS"
    )  # AWS, GCP, Azure
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="us-east-1")
    resource: Mapped[str] = mapped_column(
        String(255), nullable=False, default="s3://cloudpulse-prod-backups"
    )
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Critical"
    )  # Critical, High, Medium, Low
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Storage"
    )  # IAM, Network, Storage, Database, Secrets
    compliance_framework: Mapped[str] = mapped_column(
        String(100), nullable=False, default="CIS"
    )  # CIS, ISO 27001, SOC 2, NIST CSF, PCI DSS, HIPAA, GDPR
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    ai_analysis: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Open"
    )  # Open, In_Progress, Resolved, Ignored


class ComplianceReport(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "compliance_reports"

    framework: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )  # CIS Benchmarks, ISO 27001, SOC 2, NIST CSF, PCI DSS, HIPAA, GDPR
    overall_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=85.0
    )  # 0.0 to 100.0
    passed_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=42)
    failed_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    total_controls: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    category_scores: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
