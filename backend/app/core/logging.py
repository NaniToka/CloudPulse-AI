"""
Structured logging via structlog.

Call ``setup_logging()`` once at application startup (already done in main.py).
Then obtain loggers with ``get_logger(__name__)`` throughout the codebase.

Output format is controlled by the LOG_FORMAT env var:
  - ``json``  → machine-readable JSON (production default)
  - ``text``  → human-readable console output (development)
"""

import logging
import sys

import structlog

from app.core.config import settings


def setup_logging() -> None:
    """Configure structlog and the stdlib root logger."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
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
