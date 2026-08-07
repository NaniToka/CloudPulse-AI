"""
Digital Twin Infrastructure & Failure Simulation ORM Models.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class InfrastructureTwin(UUIDMixin, TimestampMixin, Base):
    """Virtual Digital Twin representation of production infrastructure."""

    __tablename__ = "infrastructure_twins"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, default="Primary Production Twin", index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="synchronized"
    )  # synchronized | simulating | degraded
    health_score: Mapped[int] = mapped_column(Integer, nullable=False, default=96)  # 0 - 100

    # Topology graph: nodes (VMs, K8s, DB, Redis, LB) and edges (dependencies)
    virtual_resources: Mapped[list] = mapped_column(JSON, default=list)
    topology_graph: Mapped[dict] = mapped_column(JSON, default=dict)  # { nodes: [], edges: [] }

    total_services_count: Mapped[int] = mapped_column(Integer, nullable=False, default=18)
    active_simulations_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    scenarios: Mapped[list[SimulationScenario]] = relationship(
        "SimulationScenario", back_populates="twin", cascade="all, delete-orphan"
    )
    executions: Mapped[list[SimulationExecution]] = relationship(
        "SimulationExecution", back_populates="twin", cascade="all, delete-orphan"
    )


class SimulationScenario(UUIDMixin, TimestampMixin, Base):
    """Pre-configured or custom failure injection scenario."""

    __tablename__ = "simulation_scenarios"

    twin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure_twins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Infrastructure"
    )  # Infrastructure | Database | Network | Security
    failure_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # node_failure | pod_crash | redis_outage | region_failure | traffic_surge_400 | db_latency
    target_resource: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict] = mapped_column(
        JSON, default=dict
    )  # duration_min, surge_percent, latency_multiplier, etc.
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="HIGH")

    # Relationships
    twin: Mapped[InfrastructureTwin] = relationship(
        "InfrastructureTwin", back_populates="scenarios"
    )
    executions: Mapped[list[SimulationExecution]] = relationship(
        "SimulationExecution", back_populates="scenario", cascade="all, delete-orphan"
    )


class SimulationExecution(UUIDMixin, TimestampMixin, Base):
    """Execution record for a failure simulation run."""

    __tablename__ = "simulation_executions"

    twin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure_twins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="completed"
    )  # running | completed | failed
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=12)

    # Blast Radius & Business Impact results
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=78)  # 0 - 100
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.92
    )  # 0.0 - 1.0
    financial_impact_usd: Mapped[float] = mapped_column(Float, nullable=False, default=4500.0)
    estimated_recovery_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=18)

    affected_services: Mapped[list] = mapped_column(
        JSON, default=list
    )  # ["checkout-svc", "auth-api", "postgres-primary"]
    blast_radius: Mapped[dict] = mapped_column(
        JSON, default=dict
    )  # { direct_impact: [], cascade_impact: [] }
    predicted_timeline: Mapped[list] = mapped_column(
        JSON, default=list
    )  # minute-by-minute failure progression
    recovery_steps: Mapped[list] = mapped_column(
        JSON, default=list
    )  # step-by-step mitigation actions

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    twin: Mapped[InfrastructureTwin] = relationship(
        "InfrastructureTwin", back_populates="executions"
    )
    scenario: Mapped[SimulationScenario] = relationship(
        "SimulationScenario", back_populates="executions"
    )


class WhatIfQuery(UUIDMixin, TimestampMixin, Base):
    """Natural language What-If scenario assessment powered by Gemini AI."""

    __tablename__ = "what_if_queries"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    impact_summary: Mapped[str] = mapped_column(Text, nullable=False)
    predicted_risk_level: Mapped[str] = mapped_column(String(50), nullable=False, default="HIGH")
    financial_risk_estimate: Mapped[str] = mapped_column(
        String(100), nullable=False, default="$12,000 / hr"
    )
    affected_components: Mapped[list] = mapped_column(JSON, default=list)
    mitigations: Mapped[list] = mapped_column(JSON, default=list)
