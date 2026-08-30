"""
Structured logging via structlog.

Call ``setup_logging()`` once at application startup (already done in main.py).
Then obtain loggers with ``get_logger(__name__)`` throughout the codebase.

Output format is controlled by the LOG_FORMAT env var:
  - ``json``  → machine-readable JSON (production default)
  - ``text``  → human-readable console output (development)
"""

import logging
import re
import sys
from typing import Any

import structlog

from app.core.config import settings

SENSITIVE_PATTERNS = [
    (re.compile(r"://([^:@\s]+):([^@\s]+)@"), r"://\1:***@"),  # DB/Redis connection string passwords
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-\._~\+\/]+=*", re.IGNORECASE), r"\1[REDACTED]"),
    (re.compile(r"(api[_\-]?key|secret[_\-]?key|password|token)\s*=\s*['\"]?[^\s'\"]+", re.IGNORECASE), r"\1=[REDACTED]"),
]


def sanitize_error_message(error: Exception | str | None) -> str:
    """Sanitize error messages to prevent credential, secret, or database URI leaks."""
    if error is None:
        return "Unknown error"
    msg = str(error)
    secrets_to_redact = (
        settings.SECRET_KEY,
        settings.JWT_SECRET_KEY,
        settings.effective_secret_key,
        settings.GEMINI_API_KEY,
    )
    for secret_val in secrets_to_redact:
        if (
            secret_val
            and len(secret_val) > 4
            and secret_val not in ("your_key_here", "your_gemini_api_key_here", "dummy", "secret")
            and secret_val in msg
        ):
            msg = msg.replace(secret_val, "[REDACTED]")
    for pattern, replacement in SENSITIVE_PATTERNS:
        msg = pattern.sub(replacement, msg)
    return msg


def _sanitize_data_structure(data: Any) -> Any:
    """Recursively sanitize strings and redact sensitive keys inside data structures."""
    if isinstance(data, str):
        return sanitize_error_message(data)
    if isinstance(data, dict):
        sanitized: dict[str, Any] = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if any(
                sensitive in key_lower
                for sensitive in ("password", "secret", "token", "api_key", "authorization", "cookie")
            ):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = _sanitize_data_structure(v)
        return sanitized
    if isinstance(data, (list, tuple)):
        sanitized_list = [_sanitize_data_structure(item) for item in data]
        return type(data)(sanitized_list)
    return data


def redact_sensitive_data(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Structlog processor masking secrets, JWT tokens, and connection URIs from log dicts."""
    for key, val in list(event_dict.items()):
        event_dict[key] = _sanitize_data_structure(val)
    return event_dict


def setup_logging() -> None:
    """Configure structlog and the stdlib root logger."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        redact_sensitive_data,
    ]

    if settings.LOG_FORMAT == "json":
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level=log_level,
    )

    # Suppress noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(
            logging.WARNING if settings.is_production else logging.INFO
        )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger for *name*."""
    return structlog.get_logger(name)

