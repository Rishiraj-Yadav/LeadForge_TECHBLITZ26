"""Database connection via MongoDB (Motor + Beanie).

Client creation is LAZY — it happens inside init_mongodb() at startup,
not at module-import time.  This avoids hanging when the module is loaded.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import get_settings

# ── Module-level state (set during init_mongodb) ──
_client: AsyncIOMotorClient | None = None
_db = None


def _get_db_name(url: str) -> str:
    """Extract database name from MongoDB URI, default to 'leadforge'."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    db_name = parsed.path.lstrip("/")
    return db_name if db_name else "leadforge"


async def init_mongodb():
    """Create the Motor client and initialize Beanie ODM with all document models.

    Everything happens here so that nothing blocks at import time.
    """
    global _client, _db
    settings = get_settings()

    if not settings.MONGODB_URL or not settings.MONGODB_URL.strip():
        print("❌ MONGODB_URL is not set in .env — database disabled")
        return

    db_name = _get_db_name(settings.MONGODB_URL)
    print(f"🔗 Connecting to MongoDB (db: {db_name}) …")

    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000,
        )
        _db = _client[db_name]

        # Force a real round-trip so we know the cluster is reachable.
        await asyncio.wait_for(_client.admin.command("ping"), timeout=8)
        print("✅ MongoDB ping successful")

    except asyncio.TimeoutError:
        print("⚠️  MongoDB ping timed out (8 s) — continuing without DB")
        print("   💡 Check that your MONGODB_URL is reachable")
        _client = None
        _db = None
        return
    except Exception as exc:
        print(f"⚠️  MongoDB connection error: {exc} — continuing without DB")
        _client = None
        _db = None
        return

    # ── Init Beanie ──
    from app.models.business import Business
    from app.models.lead import Lead
    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.user import User

    try:
        await asyncio.wait_for(
            init_beanie(
                database=_db,
                document_models=[Business, Lead, Conversation, Message, User],
            ),
            timeout=10,
        )
        print("✅ MongoDB initialized successfully (Beanie ODM ready)")
    except asyncio.TimeoutError:
        print("⚠️  Beanie init timed out after 10 s — continuing without DB")
        _client = None
        _db = None
    except Exception as exc:
        print(f"⚠️  Beanie init error: {exc} — continuing anyway")


def get_db():
    """Return the Motor database instance."""
    if _db is None:
        raise RuntimeError("Database is not configured. Set MONGODB_URL in backend/.env")
    return _db