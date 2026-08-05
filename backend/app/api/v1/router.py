"""
API v1 root router.

All route groups are registered here with their prefixes and tags.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, aiops, auth, cost, incidents, logs, metrics, predictions, rag_chat, runbooks, security, traces, users

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
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
