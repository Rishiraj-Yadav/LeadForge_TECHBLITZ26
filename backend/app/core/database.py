"""Database connection via Supabase + SQLAlchemy."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from supabase import create_client, Client as SupabaseClient

from app.config import get_settings

settings = get_settings()

# ── SQLAlchemy async engine ──
if settings.DATABASE_URL:
    _db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(_db_url, echo=settings.DEBUG, pool_size=20, max_overflow=10)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
else:
    engine = None
    async_session = None

class Base(DeclarativeBase):
    pass


async def init_db():
    """Create tables (dev only — use Alembic in production)."""
    if engine is None:
        print("Warning: DATABASE_URL is not set. Skipping DB initialization.")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yields an async database session."""
    if async_session is None:
        raise RuntimeError("Database URL not configured")
        
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Supabase client (for Auth, Storage, Realtime) ──
_supabase: SupabaseClient | None = None


def get_supabase() -> SupabaseClient:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase
