"""Background worker for notification jobs."""

from app.core.queue import worker_loop


async def handle_notification(payload: dict):
    print(f"Processing notification job: {payload}")


async def run_notification_worker():
    await worker_loop("notification", handle_notification)
