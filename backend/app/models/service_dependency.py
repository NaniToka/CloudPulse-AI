"""
ServiceNode and ServiceDependency ORM Models for AI Service Dependency & Root-Cause Intelligence Engine.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class ServiceNode(UUIDMixin, TimestampMixin, Base):
    """
    Represents a discrete infrastructure or application node in the Service Dependency Graph.
    Nodes can represent services, APIs, databases, queues, Kubernetes workloads, or cloud resources.
    """

    __tablename__ = "service_nodes"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="service", index=True
    )  # service, api, database, queue, k8s_workload, cloud_resource, external
    environment: Mapped[str] = mapped_column(
        String(50), nullable=False, default="production", index=True
    )  # production, staging, dev, sandbox
    region: Mapped[str] = mapped_column(
        String(50), nullable=False, default="us-east-1", index=True
    )  # us-east-1, us-west-2, eu-west-1, global
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="HEALTHY", index=True
    )  # HEALTHY, DEGRADED, CRITICAL, UNKNOWN
    health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)  # 0 - 100
    error_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0 - 100.0%
    latency_p99_ms: Mapped[float] = mapped_column(Float, nullable=False, default=45.0)
    request_rate: Mapped[float] = mapped_column(Float, nullable=False, default=120.0)  # req/sec
    active_incidents_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)

    # Relationships to outbound and inbound dependencies
    outbound_dependencies: Mapped[list["ServiceDependency"]] = relationship(
        "ServiceDependency",
        foreign_keys="[ServiceDependency.source_service_id]",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    inbound_dependencies: Mapped[list["ServiceDependency"]] = relationship(
        "ServiceDependency",
        foreign_keys="[ServiceDependency.target_service_id]",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )


class ServiceDependency(UUIDMixin, TimestampMixin, Base):
    """
    Represents a directed causal dependency relationship (source_service -> target_service).
    Includes protocol, discovery telemetry, multi-modal confidence score, latency, and error metrics.
    """

    __tablename__ = "service_dependencies"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    source_service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_nodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    target_service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_nodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    source_service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_service: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dependency_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="http", index=True
    )  # http, database, queue, network, kubernetes, cloud_resource, grpc, internal
    protocol: Mapped[str] = mapped_column(
        String(50), nullable=False, default="HTTP/1.1"
    )  # HTTP/1.1, HTTP/2, gRPC, PostgreSQL, Redis, AMQP, Kafka, TCP
    discovered_from: Mapped[str] = mapped_column(
        String(50), nullable=False, default="traces"
    )  # traces, logs, metrics, kubernetes, cloud_resources, config, manual
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)  # 0.0 - 1.0
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=42.5)
    avg_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=42.5)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    request_rate: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1250)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    evidence_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    # Node ORM Relationships
    source_node: Mapped["ServiceNode | None"] = relationship(
        "ServiceNode",
        foreign_keys=[source_service_id],
        back_populates="outbound_dependencies",
    )
    target_node: Mapped["ServiceNode | None"] = relationship(
        "ServiceNode",
        foreign_keys=[target_service_id],
        back_populates="inbound_dependencies",
    )
