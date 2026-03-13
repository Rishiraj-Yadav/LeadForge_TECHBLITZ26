"""Background worker for follow-up jobs."""

from app.core.queue import worker_loop


async def handle_followup(payload: dict):
    print(f"Processing follow-up job: {payload}")


async def run_followup_worker():
    await worker_loop("followup", handle_followup)
