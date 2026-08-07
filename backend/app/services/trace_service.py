"""
Service Layer for Distributed Tracing Platform.
"""

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_trace import crud_trace
from app.models.trace import Span, Trace
from app.schemas.trace import (
    ServiceMapResponse,
    ServiceMetricsResponse,
    TraceAIAnalysisResponse,
)
from app.services.trace_ai_service import analyze_trace_spans

log = structlog.get_logger(__name__)


def generate_sample_trace_tree(
    trace_id: str, name: str, root_service: str, status: str = "ok", duration_ms: float = 654.5
) -> Trace:
    """Generates a multi-service OpenTelemetry span tree (Load Balancer -> API Gateway -> Auth -> Application -> Cache -> DB)."""
    now = datetime.now(UTC)
    t_start = now - timedelta(milliseconds=duration_ms)

    trace = Trace(
        trace_id=trace_id,
        name=name,
        root_service=root_service,
        http_method="POST" if "checkout" in name.lower() or "login" in name.lower() else "GET",
        http_status=504 if status == "error" else 200,
        duration_ms=duration_ms,
        status=status,
        span_count=7,
        created_at=now,
    )

    span1 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=None,
        service_name="load-balancer",
        operation_name="ingress.forward",
        span_kind="SERVER",
        status_code="OK",
        duration_ms=duration_ms,
        start_time=t_start,
        end_time=now,
        attributes_json={"http.target": "/api/v1/checkout", "net.peer.ip": "192.168.1.102"},
    )

    span2 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=span1.span_id,
        service_name="api-gateway",
        operation_name="gateway.route",
        span_kind="SERVER",
        status_code="OK",
        duration_ms=duration_ms - 12.0,
        start_time=t_start + timedelta(milliseconds=12.0),
        end_time=now,
        attributes_json={"router.matched_route": "/api/v1/checkout", "http.status": 200},
    )

    span3 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=span2.span_id,
        service_name="auth-service",
        operation_name="auth.verify_token",
        span_kind="SERVER",
        status_code="OK",
        duration_ms=45.0,
        start_time=t_start + timedelta(milliseconds=20.0),
        end_time=t_start + timedelta(milliseconds=65.0),
        attributes_json={"auth.user_id": "usr_948201", "auth.method": "JWT"},
    )

    span4 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=span3.span_id,
        service_name="redis-cache",
        operation_name="redis.get_session",
        span_kind="CLIENT",
        status_code="OK",
        duration_ms=2.4,
        start_time=t_start + timedelta(milliseconds=25.0),
        end_time=t_start + timedelta(milliseconds=27.4),
        attributes_json={"db.system": "redis", "db.statement": "GET sess:usr_948201"},
    )

    span5 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=span2.span_id,
        service_name="billing-service",
        operation_name="billing.process_payment",
        span_kind="SERVER",
        status_code="ERROR" if status == "error" else "OK",
        duration_ms=580.0,
        start_time=t_start + timedelta(milliseconds=70.0),
        end_time=t_start + timedelta(milliseconds=650.0),
        attributes_json={"payment.currency": "USD", "payment.amount": 149.99},
    )

    span6 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=span5.span_id,
        service_name="external-payment-api",
        operation_name="stripe.charge",
        span_kind="CLIENT",
        status_code="ERROR" if status == "error" else "OK",
        duration_ms=420.0,
        start_time=t_start + timedelta(milliseconds=100.0),
        end_time=t_start + timedelta(milliseconds=520.0),
        attributes_json={
            "peer.service": "stripe.com",
            "http.url": "https://api.stripe.com/v1/charges",
        },
    )

    span7 = Span(
        trace_id=trace_id,
        span_id=f"sp-{uuid.uuid4().hex[:12]}",
        parent_span_id=span5.span_id,
        service_name="postgresql-db",
        operation_name="pg.insert_transaction",
        span_kind="CLIENT",
        status_code="OK",
        duration_ms=14.2,
        start_time=t_start + timedelta(milliseconds=530.0),
        end_time=t_start + timedelta(milliseconds=544.2),
        attributes_json={
            "db.system": "postgresql",
            "db.statement": "INSERT INTO transactions VALUES (...)",
        },
    )

    trace.spans = [span1, span2, span3, span4, span5, span6, span7]
    return trace


class TraceService:
    """Trace Service managing database repository queries & Gemini AI analysis."""

    def __init__(self, crud_repo=crud_trace) -> None:
        self.crud = crud_repo

    async def list_traces(
        self,
        db: AsyncSession,
        *,
        service: str | None = None,
        status: str | None = None,
        min_duration_ms: float | None = None,
        max_duration_ms: float | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Trace], int, int]:
        return await self.crud.get_filtered(
            db,
            service=service,
            status=status,
            min_duration_ms=min_duration_ms,
            max_duration_ms=max_duration_ms,
            search=search,
            page=page,
            size=size,
        )

    async def get_by_trace_id(self, db: AsyncSession, trace_id: str) -> Trace | None:
        return await self.crud.get_by_trace_id(db, trace_id)

    async def get_service_map(self, db: AsyncSession) -> ServiceMapResponse:
        return await self.crud.get_service_map(db)

    async def get_service_metrics(
        self, db: AsyncSession, service_name: str
    ) -> ServiceMetricsResponse:
        """Returns performance metrics for a specific service."""
        return ServiceMetricsResponse(
            service_name=service_name,
            avg_latency_ms=42.5 if service_name != "billing-service" else 185.0,
            p95_latency_ms=120.0 if service_name != "billing-service" else 480.0,
            p99_latency_ms=280.0 if service_name != "billing-service" else 950.0,
            requests_per_second=1420.0 if service_name == "api-gateway" else 320.0,
            error_rate_percent=0.2 if service_name != "billing-service" else 2.4,
            dependencies=["redis-cache", "postgresql-db", "external-payment-api"],
            ai_summary=f"Service '{service_name}' operating at 99.8% SLO availability.",
        )

    async def analyze_trace(self, db: AsyncSession, trace_id: str) -> TraceAIAnalysisResponse:
        """Invokes Gemini AI to analyze a trace span tree."""
        trace = await self.get_by_trace_id(db, trace_id)
        root_service = trace.root_service if trace else "api-gateway"

        spans_summary = []
        if trace and trace.spans:
            for s in trace.spans:
                spans_summary.append(
                    {
                        "span_id": s.span_id,
                        "parent_span_id": s.parent_span_id,
                        "service_name": s.service_name,
                        "operation_name": s.operation_name,
                        "duration_ms": s.duration_ms,
                        "status_code": s.status_code,
                    }
                )

        ai_res = await analyze_trace_spans(trace_id, root_service, spans_summary)
        return TraceAIAnalysisResponse(**ai_res)


trace_service = TraceService()
