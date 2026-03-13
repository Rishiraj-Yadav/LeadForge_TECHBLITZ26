"""Input normalization helpers for multi-source lead capture."""

from typing import Any


def parse_telegram_message(payload: dict) -> dict[str, Any]:
    return {
        "source": "telegram",
        "customer_name": payload.get("from_username") or payload.get("from_name"),
        "customer_phone": None,
        "customer_email": None,
        "message": payload.get("text", ""),
        "details": {
            "telegram_chat_id": payload.get("chat_id"),
            "telegram_username": payload.get("from_username"),
        },
    }


def parse_instagram_message(payload: dict) -> dict[str, Any]:
    return {
        "source": "instagram",
        "customer_name": payload.get("sender_id"),
        "message": payload.get("text", ""),
        "details": {},
    }


def parse_email_message(payload: dict) -> dict[str, Any]:
    return {
        "source": "email",
        "customer_name": payload.get("from_name"),
        "customer_email": payload.get("from_email"),
        "message": payload.get("body", ""),
        "details": {"subject": payload.get("subject")},
    }


def parse_form_submission(payload: dict) -> dict[str, Any]:
    return {
        "source": "form",
        "customer_name": payload.get("name"),
        "customer_phone": payload.get("phone"),
        "customer_email": payload.get("email"),
        "message": payload.get("message", ""),
        "details": {"source_url": payload.get("source_url")},
    }
