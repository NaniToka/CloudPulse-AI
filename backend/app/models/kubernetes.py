"""
Kubernetes & Container Intelligence ORM Models.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class K8sCluster(UUIDMixin, TimestampMixin, Base):
    """Monitored Kubernetes Cluster (GKE, EKS, AKS, Self-Hosted)."""

    __tablename__ = "k8s_clusters"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="GKE"
    )  # GKE | EKS | AKS | Self-Hosted
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.29.3")
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="us-central1")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="healthy"
    )  # healthy | warning | critical

    # Capacity & Counts
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    pod_count: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    cpu_capacity_cores: Mapped[float] = mapped_column(Float, nullable=False, default=48.0)
    cpu_usage_cores: Mapped[float] = mapped_column(Float, nullable=False, default=18.4)
    memory_capacity_gb: Mapped[float] = mapped_column(Float, nullable=False, default=192.0)
    memory_usage_gb: Mapped[float] = mapped_column(Float, nullable=False, default=112.5)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    nodes: Mapped[list[K8sNode]] = relationship(
        "K8sNode", back_populates="cluster", cascade="all, delete-orphan"
    )
    pods: Mapped[list[K8sPod]] = relationship(
        "K8sPod", back_populates="cluster", cascade="all, delete-orphan"
    )
    deployments: Mapped[list[K8sDeployment]] = relationship(
        "K8sDeployment", back_populates="cluster", cascade="all, delete-orphan"
    )


class K8sNode(UUIDMixin, TimestampMixin, Base):
    """Kubernetes Node."""

    __tablename__ = "k8s_nodes"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="worker"
    )  # control-plane | worker
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Ready"
    )  # Ready | NotReady | SchedulingDisabled
    instance_type: Mapped[str] = mapped_column(String(100), nullable=False, default="n2-standard-4")
    internal_ip: Mapped[str] = mapped_column(String(45), nullable=False, default="10.128.0.12")
    kubelet_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.29.3")

    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False, default=45.0)
    memory_percent: Mapped[float] = mapped_column(Float, nullable=False, default=62.0)
    disk_percent: Mapped[float] = mapped_column(Float, nullable=False, default=38.0)
    pod_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=110)
    pods_running: Mapped[int] = mapped_column(Integer, nullable=False, default=18)

    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("k8s_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    cluster: Mapped[K8sCluster] = relationship("K8sCluster", back_populates="nodes")
    pods: Mapped[list[K8sPod]] = relationship("K8sPod", back_populates="node")


class K8sPod(UUIDMixin, TimestampMixin, Base):
    """Kubernetes Pod telemetry."""

    __tablename__ = "k8s_pods"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(
        String(100), nullable=False, default="default", index=True
    )
    deployment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Running"
    )  # Running | Pending | CrashLoopBackOff | OOMKilled | ImagePullBackOff
    restart_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    cpu_usage_m: Mapped[float] = mapped_column(Float, nullable=False, default=120.0)  # millicores
    memory_usage_mb: Mapped[float] = mapped_column(Float, nullable=False, default=256.0)  # MB
    container_images: Mapped[dict] = mapped_column(JSON, default=dict)

    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("k8s_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("k8s_nodes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    cluster: Mapped[K8sCluster] = relationship("K8sCluster", back_populates="pods")
    node: Mapped[K8sNode | None] = relationship("K8sNode", back_populates="pods")


class K8sDeployment(UUIDMixin, TimestampMixin, Base):
    """Kubernetes Deployment workloads."""

    __tablename__ = "k8s_deployments"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    desired_replicas: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    ready_replicas: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    updated_replicas: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False, default="RollingUpdate")
    image: Mapped[str] = mapped_column(
        String(500), nullable=False, default="gcr.io/cloudpulse/api-gateway:v2.4.1"
    )

    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("k8s_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    cluster: Mapped[K8sCluster] = relationship("K8sCluster", back_populates="deployments")


class K8sEvent(UUIDMixin, TimestampMixin, Base):
    """Kubernetes Warning & Normal cluster events."""

    __tablename__ = "k8s_events"

    event_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Normal"
    )  # Normal | Warning
    reason: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # OOMKilled | FailedScheduling | BackOff | Unhealthy
    object_kind: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Pod"
    )  # Pod | Node | Deployment
    object_name: Mapped[str] = mapped_column(String(255), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
