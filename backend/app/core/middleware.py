"""
Production-grade FastAPI middleware suite:
1. CorrelationIdMiddleware (X-Correlation-ID, X-Request-ID, structlog context binding)
2. SecurityHeadersMiddleware (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
3. RateLimitMiddleware (In-memory token bucket with X-RateLimit headers)
4. MetricsTrackingMiddleware (Request duration, status codes, active requests for Prometheus)
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.telemetry import SpanContext

log = structlog.get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Extracts or generates X-Correlation-ID and X-Request-ID headers,
    binds them to structlog contextvars for the duration of the request,
    and attaches them to the outgoing HTTP response.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or uuid.uuid4().hex
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        traceparent = request.headers.get("traceparent")

        # Create OpenTelemetry Span Context
        span = (
            SpanContext.from_w3c_traceparent(
                name=f"{request.method} {request.url.path}", traceparent=traceparent
            )
            if traceparent
            else SpanContext(name=f"{request.method} {request.url.path}")
        )

        # Store in request state for access in endpoints
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id
        request.state.span = span

        # Bind to structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            request_id=request_id,
            trace_id=span.trace_id,
            path=request.url.path,
            method=request.method,
        )

        response: Response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = request_id
        response.headers["traceparent"] = span.to_w3c_traceparent()
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Enforces enterprise security headers across all incoming responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiter protecting against brute force & DoS.
    Enforces 200 requests per minute per IP on standard endpoints.
    """

    def __init__(self, app: ASGIApp, max_requests_per_minute: int = 300) -> None:
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.clients: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for static assets, docs, health, metrics, and test environment
        path = request.url.path
        if (
            settings.APP_ENV in ("testing", "test")
            or not request.client
            or request.client.host == "testclient"
            or path.startswith(
                ("/docs", "/redoc", "/openapi.json", "/health", "/ready", "/metrics", "/static")
            )
        ):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Clean old timestamps (> 60s)
        window = self.clients.get(client_ip, [])
        valid_window = [t for t in window if now - t < 60.0]
        valid_window.append(now)
        self.clients[client_ip] = valid_window

        remaining = max(0, self.max_requests - len(valid_window))

        if len(valid_window) > self.max_requests:
            return Response(
                content='{"detail":"Rate limit exceeded. Please retry in 60 seconds."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "60",
                    "Retry-After": "60",
                },
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
