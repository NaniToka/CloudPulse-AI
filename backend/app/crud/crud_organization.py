"""
Organization CRUD operations.

``create_with_unique_slug`` derives a URL-safe slug from the name and
appends an integer suffix when collisions occur.
"""

import re
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationResponse

log = structlog.get_logger(__name__)


def _slugify(name: str) -> str:
    """Convert *name* to a lowercase, hyphen-separated slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationResponse]):

    async def get_by_slug(
        self, db: AsyncSession, *, slug: str
    ) -> Optional[Organization]:
        result = await db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create_with_unique_slug(
        self,
        db: AsyncSession,
        *,
        name: str,
        team_size: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> Organization:
        """
        Create an organization ensuring its slug is unique.

        Tries ``<base-slug>``, then ``<base-slug>-1``, ``<base-slug>-2``, …
        """
        base = _slugify(name)
        slug = base
        counter = 1
        while await self.get_by_slug(db, slug=slug):
            slug = f"{base}-{counter}"
            counter += 1

        org = Organization(
            name=name,
            slug=slug,
            team_size=team_size,
            industry=industry,
        )
        db.add(org)
        await db.flush()
        await db.refresh(org)
        log.info("org_created", org_id=str(org.id), slug=slug)
        return org


# Singleton instance
crud_organization = CRUDOrganization(Organization)
