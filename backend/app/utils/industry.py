"""Lightweight conversational field extraction by industry-neutral heuristics."""

import re


FIELD_PATTERNS = {
    "guest_count": r"(\d{1,4})(?:\s*[-to]{0,3}\s*\d{1,4})?\s*(?:people|guests|persons)",
    "budget": r"(?:\$|₹|€|£)\s?[\d,]+|\d[\d,]*(?:\s?)(?:usd|inr|eur|dollars|rupees)",
    "event_type": r"birthday|party|wedding|meeting|conference|stay|getaway|booking|room",
    "time": r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|morning|evening|lunch|afternoon",
}


def infer_details_from_message(message: str, current_details: dict | None = None) -> dict:
    details = dict(current_details or {})
    lowered = message.lower()

    if "guest_count" not in details:
        match = re.search(FIELD_PATTERNS["guest_count"], lowered, re.IGNORECASE)
        if match:
            details["guest_count"] = match.group(0)

    if "budget" not in details:
        match = re.search(FIELD_PATTERNS["budget"], message, re.IGNORECASE)
        if match:
            details["budget"] = match.group(0)

    if "event_type" not in details:
        match = re.search(FIELD_PATTERNS["event_type"], lowered, re.IGNORECASE)
        if match:
            details["event_type"] = match.group(0).replace("booking", "hotel_booking")

    if "time" not in details:
        match = re.search(FIELD_PATTERNS["time"], lowered, re.IGNORECASE)
        if match:
            details["time"] = match.group(0)

    if "industry_hint" not in details:
        if any(word in lowered for word in ["room", "hotel", "stay", "suite"]):
            details["industry_hint"] = "hospitality"
        elif any(word in lowered for word in ["party", "catering", "birthday", "guests"]):
            details["industry_hint"] = "events"
        elif any(word in lowered for word in ["property", "apartment", "rent", "buy"]):
            details["industry_hint"] = "real_estate"

    return details


def missing_capture_fields(details: dict) -> list[str]:
    core_fields = ["event_type", "guest_count", "time"] if details.get("industry_hint") == "events" else []
    if details.get("industry_hint") == "hospitality":
        core_fields = ["guest_count", "date"]
    return [field for field in core_fields if not details.get(field)]


def next_capture_question(details: dict) -> str | None:
    missing = missing_capture_fields(details)
    if not missing:
        return None
    prompts = {
        "event_type": "What kind of event are you planning?",
        "guest_count": "How many guests or people are you planning for?",
        "time": "What time works best for you?",
        "date": "Which date are you considering?",
    }
    return prompts.get(missing[0])