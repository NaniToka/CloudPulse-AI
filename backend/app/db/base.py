"""
SQLAlchemy declarative base — import all models here so Alembic can detect them.
"""

from app.db.base_class import Base  # noqa: F401

# Import all models to register them with SQLAlchemy metadata
from app.models.user import User  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.resource import Resource  # noqa: F401
from app.models.incident import Incident  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.chat_session import ChatSession  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.log_analysis import LogAnalysis  # noqa: F401
from app.models.cloud_cost import CloudCost, OptimizationRecommendation  # noqa: F401
from app.models.prediction import Prediction  # noqa: F401
from app.models.metric import MetricPoint  # noqa: F401
from app.models.trace import Trace, Span, ServiceDependency  # noqa: F401
from app.models.runbook import Runbook, AutomationStep, RunbookExecution  # noqa: F401
from app.models.security import SecurityScan, ComplianceReport  # noqa: F401
from app.models.aiops import AIOpsAgent, AgentTask, AgentRecommendation, AgentExecution  # noqa: F401
from app.models.tenant import Team, Project, OrganizationMember, TeamMember, Invitation, AuditLog  # noqa: F401
from app.models.cloud_account import CloudAccount  # noqa: F401
from app.models.cloud_resource import CloudResource  # noqa: F401
from app.models.cloud_region import CloudRegion  # noqa: F401
