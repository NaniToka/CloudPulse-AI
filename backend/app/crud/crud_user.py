"""
User CRUD operations.

The ``create`` method hashes passwords before persisting.  The ``authenticate``
method performs constant-time password verification to resist timing attacks.
"""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

log = structlog.get_logger(__name__)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """Fetch a user by email (case-insensitive, trimmed)."""
        canonical = email.lower().strip()
        result = await db.execute(select(User).where(User.email == canonical))
        return result.scalar_one_or_none()

    async def create(  # type: ignore[override]
        self, db: AsyncSession, *, obj_in: UserCreate
    ) -> User:
        """
        Create a user and hash the password.

        Overrides the base ``create`` so password hashing happens before flush.
        """
        user = User(
            email=obj_in.email.lower().strip(),
            hashed_password=hash_password(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role=obj_in.role,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        log.info("user_created", user_id=str(user.id), email=user.email)
        return user

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> User | None:
        """
        Verify *email* + *password* combo.

        Returns the User on success, None on failure.  Logs unsuccessful
        attempts at INFO level (rate limiting / alerting should happen elsewhere).
        """
        user = await self.get_by_email(db, email=email)
        if user is None:
            log.info("auth_failed_no_user", email=email)
            return None

        if not verify_password(password, user.hashed_password):
            log.info("auth_failed_bad_password", user_id=str(user.id))
            return None

        log.info("auth_success", user_id=str(user.id))
        return user

    async def set_organization(
        self, db: AsyncSession, *, user: User, organization_id: UUID
    ) -> User:
        """Link a user to an organization."""
        user.organization_id = organization_id
        db.add(user)
        await db.flush()
        await db.refresh(user)
        log.info(
            "user_org_linked",
            user_id=str(user.id),
            organization_id=str(organization_id),
        )
        return user

    async def activate(self, db: AsyncSession, *, user: User) -> User:
        """Mark a user as verified (e.g., after email confirmation)."""
        user.is_verified = True
        db.add(user)
        await db.flush()
        await db.refresh(user)
        log.info("user_verified", user_id=str(user.id))
        return user


# Singleton instance
crud_user = CRUDUser(User)
