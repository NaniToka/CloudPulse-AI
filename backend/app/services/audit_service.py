"""
Security Audit Service for Enterprise Compliance and Activity Tracking.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import AuditLog

log = structlog.get_logger(__name__)


class AuditLogService:
    """Records security audit events to PostgreSQL and structlog for compliance."""

    async def log_event(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        now = datetime.now(UTC)
        record = AuditLog(
            id=uuid.uuid4(),
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            details=details or {},
            created_at=now,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        log.info(
            "security_audit_event",
            action=action,
            organization_id=str(organization_id),
            user_id=str(user_id) if user_id else None,
            details=details,
        )
        return record


audit_service = AuditLogService()
