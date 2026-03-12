"""Redis cache + pub-sub helper."""

import redis.asyncio as aioredis
from app.config import get_settings

settings = get_settings()

_redis: aioredis.Redis | None = None


async def init_redis():
    global _redis
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialised — call init_redis() first")
    return _redis


async def cache_set(key: str, value: str, ttl: int = 3600):
    r = get_redis()
    await r.set(key, value, ex=ttl)


async def cache_get(key: str) -> str | None:
    r = get_redis()
    return await r.get(key)


async def cache_delete(key: str):
    r = get_redis()
    await r.delete(key)


async def publish(channel: str, message: str):
    r = get_redis()
    await r.publish(channel, message)
