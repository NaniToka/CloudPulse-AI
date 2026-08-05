"""
AIOpsAgent, AgentTask, AgentRecommendation, and AgentExecution models for Autonomous AIOps Agent.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, JSON, Float, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDMixin, TimestampMixin


class AIOpsAgent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "aiops_agents"

    agent_name: Mapped[str] = mapped_column(String(255), nullable=False, default="CloudPulse Autonomous Core")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Autonomous")  # Active, Autonomous, Paused
    current_phase: Mapped[str] = mapped_column(String(50), nullable=False, default="Observe")  # Observe, Detect, Analyze, Plan, Recommend, Verify
    health_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Healthy")  # Healthy, Degraded, Anomalous
    last_observation_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    tasks: Mapped[list["AgentTask"]] = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    recommendations: Mapped[list["AgentRecommendation"]] = relationship("AgentRecommendation", back_populates="agent", cascade="all, delete-orphan")


class AgentTask(UUIDMixin, Base):
    __tablename__ = "agent_tasks"

    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aiops_agents.id", ondelete="CASCADE"), nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_system: Mapped[str] = mapped_column(String(100), nullable=False)  # Metrics, Logs, Traces, Security, Cost
    status: Mapped[str] = mapped_column(String(50), default="Completed")  # Pending, In_Progress, Completed, Failed
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    agent: Mapped["AIOpsAgent"] = relationship("AIOpsAgent", back_populates="tasks")


class AgentRecommendation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agent_recommendations"

    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aiops_agents.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Anomaly_Detection")  # Anomaly_Detection, Root_Cause, Performance, Capacity_Planning, Risk_Prediction, Cost_Optimization, Security_Correlation
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="P1")  # P0, P1, P2, P3
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=True)
    business_impact: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    automation_candidates: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95)
    expected_recovery_time: Mapped[str] = mapped_column(String(100), default="10 mins")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending_Approval")  # Pending_Approval, Approved, Rejected, Executed

    agent: Mapped["AIOpsAgent"] = relationship("AIOpsAgent", back_populates="recommendations")
    executions: Mapped[list["AgentExecution"]] = relationship("AgentExecution", back_populates="recommendation", cascade="all, delete-orphan")


class AgentExecution(UUIDMixin, Base):
    __tablename__ = "agent_executions"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_recommendations.id", ondelete="CASCADE"), nullable=False)
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    approved_by: Mapped[str] = mapped_column(String(255), nullable=False, default="AIOps Autonomous Controller")
    status: Mapped[str] = mapped_column(String(50), default="Completed")
    execution_logs: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    recommendation: Mapped["AgentRecommendation"] = relationship("AgentRecommendation", back_populates="executions")
