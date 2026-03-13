"""Simple async job queue backed by Redis lists."""

import json
import asyncio
from datetime import datetime
from app.core.cache import get_redis


async def enqueue(queue_name: str, payload: dict):
    """Push a job onto a Redis list."""
    r = get_redis()
    job = {
        "payload": payload,
        "created_at": datetime.utcnow().isoformat(),
    }
    await r.rpush(f"queue:{queue_name}", json.dumps(job))


async def dequeue(queue_name: str, timeout: int = 0) -> dict | None:
    """Blocking pop from a Redis list. Returns payload dict or None."""
    r = get_redis()
    result = await r.blpop(f"queue:{queue_name}", timeout=timeout)
    if result:
        _, raw = result
        return json.loads(raw)
    return None


async def worker_loop(queue_name: str, handler):
    """Run forever, processing jobs from the given queue."""
    while True:
        job = await dequeue(queue_name, timeout=5)
        if job:
            try:
                await handler(job["payload"])
            except Exception as exc:
                # Dead-letter: push to a failed queue for inspection
                r = get_redis()
                failed = {**job, "error": str(exc)}
                await r.rpush(f"queue:{queue_name}:failed", json.dumps(failed))
        else:
            await asyncio.sleep(0.1)
