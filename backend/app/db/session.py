"""
Async SQLAlchemy engine and session factory.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs: dict = {
    "echo": settings.is_development,
    "pool_pre_ping": True,
}
if not is_sqlite:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
