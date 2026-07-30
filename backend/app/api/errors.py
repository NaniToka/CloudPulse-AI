"""
Global exception handlers.

Registered via ``register_exception_handlers(app)`` in main.py.

All error responses share the same envelope:
    { "error": "<human message>", "details": [...] }   # details optional
"""

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

log = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all custom exception handlers to *app*."""

    # ------------------------------------------------------------------
    # 422 — Pydantic / FastAPI request validation
    # ------------------------------------------------------------------
    @app.exception_handler(RequestValidationError)
    async def _request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> ORJSONResponse:
        details = []
        for error in exc.errors():
            # Drop "body" and "query" location prefixes for cleaner output
            locs = [str(loc) for loc in error["loc"] if loc not in ("body", "query")]
            details.append({
                "field": ".".join(locs) or None,
                "message": error["msg"],
                "type": error["type"],
            })
        log.info(
            "request_validation_error",
            path=str(request.url),
            method=request.method,
            detail_count=len(details),
        )
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation failed.", "details": details},
        )

    # ------------------------------------------------------------------
    # 422 — Pydantic model instantiation errors outside request parsing
    # ------------------------------------------------------------------
    @app.exception_handler(ValidationError)
    async def _pydantic_validation_handler(
        request: Request, exc: ValidationError
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation failed.", "details": exc.errors()},
        )

    # ------------------------------------------------------------------
    # HTTPException — covers 400, 401, 403, 404, 409, etc.
    # ------------------------------------------------------------------
    @app.exception_handler(HTTPException)
    async def _http_exception_handler(
        request: Request, exc: HTTPException
    ) -> ORJSONResponse:
        if exc.status_code >= 500:
            log.error(
                "http_exception",
                status=exc.status_code,
                detail=exc.detail,
                path=str(request.url),
            )
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
            headers=getattr(exc, "headers", None) or {},
        )

    # ------------------------------------------------------------------
    # 500 — Unhandled exceptions (last-resort safety net)
    # ------------------------------------------------------------------
    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> ORJSONResponse:
        log.exception(
            "unhandled_exception",
            exc_type=type(exc).__name__,
            path=str(request.url),
            method=request.method,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected internal server error occurred."},
        )
