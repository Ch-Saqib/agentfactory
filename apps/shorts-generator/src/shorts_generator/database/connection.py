"""Async database connection management for Lesson Shorts Generator."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool

from shorts_generator.core.config import settings
from shorts_generator.models import Base


def _create_engine() -> AsyncEngine:
    """Create a new async engine configured for cloud databases.

    Uses NullPool so connections are not held open between requests.
    Cloud database providers (Neon, Supabase) handle connection pooling.

    Returns:
        AsyncEngine: SQLAlchemy async engine with NullPool.
    """
    # Convert postgresql:// to postgresql+asyncpg:// for asyncpg driver
    database_url = settings.shorts_database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    # Remove sslmode from URL if present (asyncpg doesn't support it in URL)
    # We'll pass SSL via connect_args instead
    database_url = database_url.split("?")[0].split("&")[0]

    return create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging
        poolclass=NullPool,  # No local pooling - cloud handles it
        connect_args={
            "server_settings": {"jit": "off"},  # Disable JIT for better performance on Neon
            "ssl": True,  # Enable SSL for Neon (asyncpg uses this, not sslmode)
        },
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with automatic cleanup.

    This is designed for FastAPI dependency injection via Depends(get_session).

    Creates a fresh connection for each request and disposes it after.
    This pattern is ideal for:
    - Serverless environments (no persistent connections)
    - Cloud databases with external pooling (Neon, Supabase)
    - Stateless HTTP servers

    Yields:
        AsyncSession: Database session that commits on success, rolls back on error.

    Example with FastAPI:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
            # Auto-commits on exit, rolls back on exception
            # Connection is released immediately after
    """
    engine = _create_engine()
    factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        # Dispose engine to release connection back to cloud pooler
        await engine.dispose()


async def init_db() -> None:
    """Initialize database tables (for development/testing).

    Creates all tables defined in models.py if they don't exist.
    For production, use Alembic migrations instead.
    """
    engine = _create_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


# Test engine management
_test_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Get engine for testing. Creates new engine each call in production."""
    global _test_engine
    if _test_engine is None:
        _test_engine = _create_engine()
    return _test_engine


async def reset_engine() -> None:
    """Reset the test engine (for testing only).

    Call this between tests to ensure clean state.
    """
    global _test_engine
    if _test_engine is not None:
        await _test_engine.dispose()
        _test_engine = None
