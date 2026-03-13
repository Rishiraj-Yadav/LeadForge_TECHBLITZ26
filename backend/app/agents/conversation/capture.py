"""Conversational capture logic to ask only for the next missing detail."""

from app.utils.industry import infer_details_from_message, next_capture_question


def capture_next_step(message: str, details: dict | None = None) -> tuple[dict, str | None]:
    updated = infer_details_from_message(message, details)
    return updated, next_capture_question(updated)