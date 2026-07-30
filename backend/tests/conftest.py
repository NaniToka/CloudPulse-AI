"""
Pytest fixtures for the CloudPulse AI backend test suite.

Strategy
--------
- Uses SQLite in-memory via ``aiosqlite`` so tests run without a real
  PostgreSQL instance (no Docker required in CI).
- One engine is created per *session* so schema creation is cheap.
- Each test gets a fresh ``AsyncSession`` that is rolled back after the
  test completes, guaranteeing isolation between tests.
- The ``client`` fixture overrides the ``get_db`` dependency so every
  request within a test shares the same rolled-back transaction.

SQLite compatibility notes
--------------------------
- ``postgresql.UUID`` columns are silently handled by SQLAlchemy's
  generic dialect fallback (stored as CHAR(32)).
- ``postgresql.JSON`` falls back to TEXT.
- ``sa.true() / sa.false()`` server defaults are handled correctly.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.dependencies import get_db
from app.db.base import Base  # registers all models
from app.main import app

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:?check_same_thread=false"


# ---------------------------------------------------------------------------
# Engine — one per test session
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Session — fresh per test, rolled back after
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session(test_engine):
    factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# HTTPX async client — shares the test session
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
