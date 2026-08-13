"""
Rollback Engine for Autonomous Operations.
Stores previous resource state and handles explicit manual/automated rollback requests.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous import RemediationExecution
from app.services.autonomous.provider_adapters import get_provider_adapter


async def execute_rollback(
    db: AsyncSession,
    *,
    execution: RemediationExecution,
    provider: str,
    actor_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """
    Executes explicit rollback operation to restore previous resource state.
    """
    if execution.rollback_status == "NOT_SUPPORTED":
        return {
            "status": "NOT_SUPPORTED",
            "message": f"Execution {execution.id} does not support rollback.",
        }

    previous_state = execution.previous_state or {}
    adapter = get_provider_adapter(provider, execution.execution_mode)

    res = await adapter.rollback(execution.plan.affected_resource if execution.plan else "resource", previous_state)

    execution.rollback_status = "ROLLBACK_SUCCESS"
    execution.status = "ROLLED_BACK"
    execution.completed_at = datetime.now(UTC)
    if execution.plan:
        execution.plan.status = "ROLLED_BACK"

    await db.commit()
    await db.refresh(execution)

    return {
        "status": "ROLLBACK_SUCCESS",
        "execution_id": str(execution.id),
        "restored_state": previous_state,
        "details": res,
    }
