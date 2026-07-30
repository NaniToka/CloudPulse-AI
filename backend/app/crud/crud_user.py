"""User CRUD operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email.lower().strip()))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:  # type: ignore[override]
        db_obj = User(
            email=obj_in.email.lower().strip(),
            hashed_password=hash_password(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role=obj_in.role,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def set_organization(
        self, db: AsyncSession, *, user: User, organization_id: UUID
    ) -> User:
        user.organization_id = organization_id
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def activate(self, db: AsyncSession, *, user: User) -> User:
        user.is_verified = True
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user


crud_user = CRUDUser(User)
