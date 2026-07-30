"""Organization CRUD operations."""

import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationResponse


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationResponse]):

    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Optional[Organization]:
        result = await db.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()

    async def create_with_unique_slug(
        self, db: AsyncSession, *, name: str, **kwargs
    ) -> Organization:
        base_slug = _slugify(name)
        slug = base_slug
        counter = 1
        while await self.get_by_slug(db, slug=slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        org = Organization(name=name, slug=slug, **kwargs)
        db.add(org)
        await db.flush()
        await db.refresh(org)
        return org


crud_organization = CRUDOrganization(Organization)
