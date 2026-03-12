"""Serper web search client for lead research."""

import httpx

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SerperClient:
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev"
        self.headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    async def search(self, query: str, num_results: int = 5) -> dict:
        payload = {"q": query, "num": num_results}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/search", json=payload, headers=self.headers, timeout=10
            )
            resp.raise_for_status()
            logger.info(f"Serper search executed for query: {query}")
            return resp.json()

    async def company_lookup(self, company_name: str) -> dict:
        return await self.search(f"{company_name} company LinkedIn website reviews")


def get_search_client() -> SerperClient:
    return SerperClient()
