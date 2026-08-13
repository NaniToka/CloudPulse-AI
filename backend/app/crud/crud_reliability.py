"""
CRUD Repository for Service Reliability Profiles, Risks, & Recommendations.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.slo import (
    ServiceReliabilityProfile,
)


class CRUDReliability(CRUDBase[ServiceReliabilityProfile, Any, Any]):
    """CRUD operations for Service Reliability Engine 2.0."""

    async def get_all_profiles(
        self,
        db: AsyncSession,
        *,
        provider: str | None = None,
        service: str | None = None,
        status: str | None = None,
    ) -> list[ServiceReliabilityProfile]:
        """Fetch stored service reliability profiles with filtering."""
        stmt = select(ServiceReliabilityProfile)
        if provider and provider.upper() != "ALL":
            stmt = stmt.where(ServiceReliabilityProfile.provider == provider)
        if service and service.upper() != "ALL":
            stmt = stmt.where(ServiceReliabilityProfile.service_name == service)
        if status and status.upper() != "ALL":
            stmt = stmt.where(ServiceReliabilityProfile.status == status.upper())

        res = await db.execute(stmt.order_by(ServiceReliabilityProfile.reliability_score.asc()))
        return list(res.scalars().all())

    async def get_profile_by_service_id(
        self, db: AsyncSession, service_id: str
    ) -> ServiceReliabilityProfile | None:
        """Fetch single service profile by service_id."""
        stmt = select(ServiceReliabilityProfile).where(
            (ServiceReliabilityProfile.service_id == service_id)
            | (ServiceReliabilityProfile.service_name == service_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert_profile(
        self, db: AsyncSession, data: dict[str, Any]
    ) -> ServiceReliabilityProfile:
        """Create or update a service reliability profile."""
        svc_id = data.get("service_id", data.get("service_name"))
        existing = await self.get_profile_by_service_id(db, svc_id)
        if existing:
            for k, v in data.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            db.add(existing)
            await db.flush()
            await db.refresh(existing)
            return existing
        else:
            profile = ServiceReliabilityProfile(**data)
            db.add(profile)
            await db.flush()
            await db.refresh(profile)
            return profile


crud_reliability = CRUDReliability(ServiceReliabilityProfile)
