"""Database connection via MongoDB (Motor + Beanie).

Client creation is LAZY — it happens inside init_mongodb() at startup,
not at module-import time.  This avoids hanging when the module is loaded.
"""

import asyncio
import ssl
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
    """Create the Motor client and initialize Beanie ODM.

    Tries up to 3 times with increasing timeouts.
    Raises on failure so the caller (main.py) knows it didn't work.
    """
    global _client, _db
    settings = get_settings()

    if not settings.MONGODB_URL or not settings.MONGODB_URL.strip():
        print("❌ MONGODB_URL is not set in .env — database disabled")
        return

    db_name = _get_db_name(settings.MONGODB_URL)

    # Build a permissive TLS context (Atlas free-tier + Python 3.13 compat)
    try:
        import certifi
        ca_file = certifi.where()
    except ImportError:
        ca_file = None

    max_attempts = 3
    last_error = None

    for attempt in range(1, max_attempts + 1):
        timeout = 5 * attempt  # 5s, 10s, 15s
        print(f"🔗 MongoDB connect attempt {attempt}/{max_attempts} (db: {db_name}, timeout: {timeout}s) …")

        try:
            _client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=timeout * 1000,
                connectTimeoutMS=timeout * 1000,
                socketTimeoutMS=timeout * 1000,
                tls=True,
                tlsAllowInvalidCertificates=True,
                **({"tlsCAFile": ca_file} if ca_file else {}),
            )
            _db = _client[db_name]

            # Force a real round-trip so we know the cluster is reachable.
            await asyncio.wait_for(_client.admin.command("ping"), timeout=timeout)
            print("✅ MongoDB ping successful")
            break  # success — exit retry loop

        except (asyncio.TimeoutError, Exception) as exc:
            last_error = exc
            tag = "Timeout" if isinstance(exc, asyncio.TimeoutError) else type(exc).__name__
            print(f"⚠️  Attempt {attempt} failed ({tag}): {exc}")
            _client = None
            _db = None
            if attempt < max_attempts:
                wait = 2 * attempt
                print(f"   Retrying in {wait}s …")
                await asyncio.sleep(wait)

    if _db is None:
        print(f"❌ MongoDB connection failed after {max_attempts} attempts")
        raise ConnectionError(f"Cannot reach MongoDB: {last_error}")

    # ── Init Beanie ──
    from app.models.business import Business
    from app.models.lead import Lead
    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.user import User
    from app.models.onboarding_session import OnboardingSession

    await asyncio.wait_for(
        init_beanie(
            database=_db,
            document_models=[Business, Lead, Conversation, Message, User, OnboardingSession],
        ),
        timeout=15,
    )
    print("✅ MongoDB initialized successfully (Beanie ODM ready)")


def get_db():
    """Return the Motor database instance."""
    if _db is None:
        raise RuntimeError("Database is not configured. Set MONGODB_URL in backend/.env")
    return _db