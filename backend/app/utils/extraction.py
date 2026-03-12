"""Data extraction helpers for lead information."""

import re


def extract_email(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_numbers(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", text)]


def extract_budget_indicators(text: str) -> dict:
    """Look for currency amounts and budget-related keywords."""
    patterns = {
        "currency_amounts": re.findall(
            r"[\$₹€£]\s?[\d,]+(?:\.\d{2})?|\d[\d,]*(?:\.\d{2})?\s?(?:dollars|rupees|usd|inr|eur)",
            text,
            re.IGNORECASE,
        ),
        "budget_keywords": [
            kw
            for kw in ["budget", "afford", "price", "cost", "expensive", "cheap", "worth"]
            if kw in text.lower()
        ],
    }
    return patterns
