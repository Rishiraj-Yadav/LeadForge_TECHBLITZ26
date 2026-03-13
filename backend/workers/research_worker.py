"""Background worker for research jobs."""

from app.core.queue import worker_loop


async def handle_research(payload: dict):
    print(f"Processing research job: {payload}")


async def run_research_worker():
    await worker_loop("research", handle_research)
