"""
API v1 root router.

All route groups are registered here with their prefixes and tags.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    aiops,
    alerts,
    auth,
    autonomous,
    cloud,
    command_center,
    cost,
    dependencies,
    executive,
    finops_governance,
    governance,
    incidents,
    kubernetes,
    logs,
    members,
    metrics,
    notifications,
    organizations,
    predictions,
    projects,
    rag_chat,
    runbooks,
    security,
    servers,
    slo,
    sre,
    teams,
    traces,
    twin,
    users,
    workflows,
)
from app.telemetry.api import telemetry

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    telemetry.router,
    prefix="/telemetry",
    tags=["Unified Telemetry Intelligence Platform"],
)
api_router.include_router(
    twin.router,
    prefix="/twin",
    tags=["Digital Twin Infrastructure"],
)
api_router.include_router(
    workflows.router,
    prefix="/workflows",
    tags=["Enterprise Workflow Automation"],
)
api_router.include_router(
    kubernetes.router,
    prefix="/kubernetes",
    tags=["Kubernetes & Container Intelligence"],
)
api_router.include_router(
    cloud.router,
    prefix="/cloud",
    tags=["Multi-Cloud Observability"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"],
)
api_router.include_router(
    teams.router,
    prefix="/teams",
    tags=["Teams"],
)
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"],
)
api_router.include_router(
    servers.router,
    prefix="/servers",
    tags=["Servers & Infrastructure"],
)
api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Monitoring Alerts"],
)
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["User Notifications"],
)
api_router.include_router(
    members.router,
    prefix="/members",
    tags=["Members & Permissions"],
)
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Copilot"],
)
api_router.include_router(
    logs.router,
    prefix="/logs",
    tags=["Log Analyzer"],
)
api_router.include_router(
    cost.router,
    prefix="/cost",
    tags=["Cost Optimizer"],
)
api_router.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["Incident Management"],
)
api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["Predictive Analytics"],
)
api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Real-Time Observability"],
)
api_router.include_router(
    dependencies.router,
    prefix="/dependencies",
    tags=["AI Service Dependency & Root-Cause Engine"],
)
api_router.include_router(
    traces.router,
    prefix="",
    tags=["Distributed Tracing"],
)
api_router.include_router(
    rag_chat.router,
    prefix="/chat",
    tags=["RAG Infrastructure Chat"],
)
api_router.include_router(
    runbooks.router,
    prefix="/runbooks",
    tags=["Auto Remediation Center"],
)
api_router.include_router(
    security.router,
    prefix="/security",
    tags=["AI Security & Cloud Compliance"],
)
api_router.include_router(
    aiops.router,
    prefix="/aiops",
    tags=["Autonomous AIOps Agent"],
)
api_router.include_router(
    sre.router,
    prefix="/sre",
    tags=["SRE & Reliability Intelligence Center"],
)
api_router.include_router(
    governance.router,
    prefix="/governance",
    tags=["Cloud Governance & Compliance Center"],
)
api_router.include_router(
    finops_governance.router,
    prefix="/finops",
    tags=["FinOps Governance & Cost Control Center"],
)
api_router.include_router(
    executive.router,
    prefix="/executive",
    tags=["Executive Cloud Operations Command Center"],
)
api_router.include_router(
    autonomous.router,
    prefix="/autonomous",
    tags=["Autonomous Cloud Operations & Self-Healing Center"],
)
api_router.include_router(
    slo.router,
    prefix="/slo",
    tags=["Enterprise SLO, SLA & Error Budget Intelligence Center"],
)
api_router.include_router(
    command_center.router,
    prefix="/command-center",
    tags=["Enterprise Executive Intelligence & Operations Command Center"],
)
