"""
Repository for Digital Twin Infrastructure, Failure Scenarios, Executions, and What-If queries.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.digital_twin import (
    InfrastructureTwin,
    SimulationExecution,
    SimulationScenario,
    WhatIfQuery,
)


class CRUDInfrastructureTwin(CRUDBase[InfrastructureTwin, Any, Any]):
    async def get_by_user(self, db: AsyncSession, user_id: uuid.UUID) -> InfrastructureTwin | None:
        stmt = select(InfrastructureTwin).where(InfrastructureTwin.user_id == user_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


class CRUDSimulationScenario(CRUDBase[SimulationScenario, Any, Any]):
    async def get_multi_by_twin(
        self, db: AsyncSession, twin_id: uuid.UUID, category: str | None = None
    ) -> list[SimulationScenario]:
        stmt = select(SimulationScenario).where(SimulationScenario.twin_id == twin_id)
        if category and category != "all":
            stmt = stmt.where(SimulationScenario.category == category)
        res = await db.execute(stmt.order_by(SimulationScenario.created_at.desc()))
        return list(res.scalars().all())


class CRUDSimulationExecution(CRUDBase[SimulationExecution, Any, Any]):
    async def get_multi_by_twin(
        self, db: AsyncSession, twin_id: uuid.UUID, limit: int = 50
    ) -> list[SimulationExecution]:
        stmt = (
            select(SimulationExecution)
            .where(SimulationExecution.twin_id == twin_id)
            .order_by(SimulationExecution.started_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


class CRUDWhatIfQuery(CRUDBase[WhatIfQuery, Any, Any]):
    async def get_recent_by_user(
        self, db: AsyncSession, user_id: uuid.UUID, limit: int = 20
    ) -> list[WhatIfQuery]:
        stmt = (
            select(WhatIfQuery)
            .where(WhatIfQuery.user_id == user_id)
            .order_by(WhatIfQuery.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


crud_twin = CRUDInfrastructureTwin(InfrastructureTwin)
crud_scenario = CRUDSimulationScenario(SimulationScenario)
crud_execution = CRUDSimulationExecution(SimulationExecution)
crud_what_if = CRUDWhatIfQuery(WhatIfQuery)
