"""
Repository for Auto-Discovered Multi-Cloud Infrastructure Resources.
"""

import uuid
from typing import List, Optional, Any
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.cloud_resource import CloudResource


class CRUDCloudResource(CRUDBase[CloudResource, Any, Any]):
    """CRUD Repository for CloudResource."""

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        provider: Optional[str] = None,
        resource_type: Optional[str] = None,
        region: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[CloudResource]:
        stmt = select(CloudResource)
        if provider and provider != "all":
            stmt = stmt.where(CloudResource.provider == provider)
        if resource_type and resource_type != "all":
            stmt = stmt.where(CloudResource.resource_type == resource_type)
        if region and region != "all":
            stmt = stmt.where(CloudResource.region == region)
        if status and status != "all":
            stmt = stmt.where(CloudResource.status == status)
        if search:
            stmt = stmt.where(
                or_(
                    CloudResource.name.ilike(f"%{search}%"),
                    CloudResource.service.ilike(f"%{search}%"),
                    CloudResource.region.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(CloudResource.created_at.desc()).offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())


crud_cloud_resource = CRUDCloudResource(CloudResource)
