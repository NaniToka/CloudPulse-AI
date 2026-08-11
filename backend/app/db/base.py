"""
SQLAlchemy declarative base — import all models here so Alembic can detect them.
"""

from app.db.base_class import Base  # noqa: F401
from app.models.aiops import (  # noqa: F401
    AgentExecution,
    AgentRecommendation,
    AgentTask,
    AIOpsAgent,
)
from app.models.alert import Alert  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.chat_session import ChatSession  # noqa: F401
from app.models.cloud_account import CloudAccount  # noqa: F401
from app.models.cloud_cost import CloudCost, OptimizationRecommendation  # noqa: F401
from app.models.cloud_region import CloudRegion  # noqa: F401
from app.models.cloud_resource import CloudResource  # noqa: F401
from app.models.digital_twin import (  # noqa: F401
    InfrastructureTwin,
    SimulationExecution,
    SimulationScenario,
    WhatIfQuery,
)
from app.models.incident import Incident, IncidentTimelineEvent  # noqa: F401
from app.models.kubernetes import K8sCluster, K8sDeployment, K8sEvent, K8sNode, K8sPod  # noqa: F401
from app.models.log_analysis import LogAnalysis  # noqa: F401
from app.models.metric import MetricPoint  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.prediction import Prediction  # noqa: F401
from app.models.resource import Resource  # noqa: F401
from app.models.runbook import AutomationStep, Runbook, RunbookExecution  # noqa: F401
from app.models.security import ComplianceReport, SecurityScan  # noqa: F401
from app.models.telemetry import (  # noqa: F401
    MetricRecord,
    TelemetryEvent,
    TraceRecord,
)
from app.models.tenant import (  # noqa: F401
    AuditLog,
    Invitation,
    OrganizationMember,
    Project,
    Team,
    TeamMember,
)
from app.models.service_dependency import ServiceDependency, ServiceNode  # noqa: F401
from app.models.trace import Span, Trace  # noqa: F401

# Import all models to register them with SQLAlchemy metadata
from app.models.user import User  # noqa: F401
from app.models.workflow import (  # noqa: F401
    Workflow,
    WorkflowApproval,
    WorkflowExecution,
    WorkflowStepLog,
    WorkflowTemplate,
)
