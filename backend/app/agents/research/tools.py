"""Research helpers for company lookup and lightweight validation."""

from urllib.parse import urlparse

from app.services.search.serper import get_search_client
from app.utils.extraction import extract_email


async def search_company(company_name: str) -> dict:
    client = get_search_client()
    return await client.company_lookup(company_name)


def estimate_domain_age(url: str | None) -> str:
    if not url:
        return "unknown"
    host = urlparse(url if url.startswith("http") else f"https://{url}").netloc
    return f"domain found: {host}" if host else "unknown"


def validate_email_from_text(text: str) -> str | None:
    return extract_email(text)
