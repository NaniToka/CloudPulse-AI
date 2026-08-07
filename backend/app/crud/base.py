"""
Generic async CRUD base.

Provides typed ``get``, ``get_multi``, ``count``, ``create``, ``update``,
and ``delete`` operations for any SQLAlchemy model.

Concrete CRUD classes inherit from this and may override any method.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base

ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class CRUDBase(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get(self, db: AsyncSession, id: UUID) -> ModelT | None:
        """Fetch a single record by primary key. Returns None if not found."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelT]:
        """Fetch a paginated list of records."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        """Return total row count for the model's table."""
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaT) -> ModelT:
        """
        Instantiate model from *obj_in* dict and flush to the session.

        Subclasses commonly override this to handle password hashing or
        relationship setup before flush.
        """
        data = obj_in.model_dump()
        db_obj: ModelT = self.model(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelT,
        obj_in: UpdateSchemaT | dict[str, Any],
    ) -> ModelT:
        """
        Partially update *db_obj* with the fields present in *obj_in*.

        Accepts both a Pydantic schema (exclude_unset=True) and a raw dict.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: UUID) -> ModelT | None:
        """Delete a record by primary key. Returns the deleted object or None."""
        obj = await self.get(db, id)
        if obj is not None:
            await db.delete(obj)
            await db.flush()
        return obj
