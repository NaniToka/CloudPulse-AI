"""
SecurityScan and ComplianceReport SQLAlchemy models for AI Security & Compliance Center.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class SecurityScan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "security_scans"

    scan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="AWS"
    )  # AWS, GCP, Azure, Kubernetes
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="us-east-1")
    resource: Mapped[str] = mapped_column(
        String(255), nullable=False, default="s3://cloudpulse-prod-backups"
    )
    resource_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="s3_bucket"
    )  # s3_bucket, security_group, iam_role, k8s_pod, db_instance, etc.
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Critical"
    )  # Critical, High, Medium, Low, Info
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Storage"
    )  # IAM, Network, Storage, Database, Secrets, Compute, Kubernetes
    compliance_framework: Mapped[str] = mapped_column(
        String(100), nullable=False, default="CIS"
    )  # CIS, ISO 27001, SOC 2, NIST CSF, PCI DSS, HIPAA, GDPR
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=7.5)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.90)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    ai_analysis: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="OPEN"
    )  # OPEN, INVESTIGATING, MITIGATED, RESOLVED, ACCEPTED_RISK
    first_detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


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
    category_scores: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
