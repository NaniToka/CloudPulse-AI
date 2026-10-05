"""
Async SQLAlchemy engine and session factory.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _coerce_async_url(url: str) -> str:
    """
    Ensure the database URL uses an async driver.

    Render (and many other platforms) inject DATABASE_URL as
    'postgres://' or 'postgresql://' which resolve to the sync psycopg2
    driver.  SQLAlchemy's asyncio extension requires 'postgresql+asyncpg://'.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


_database_url = _coerce_async_url(settings.DATABASE_URL)
is_sqlite = _database_url.startswith("sqlite")
engine_kwargs: dict = {
    "echo": settings.is_development,
    "pool_pre_ping": True,
}
if not is_sqlite:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(
    _database_url,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
