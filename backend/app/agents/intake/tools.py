"""Input normalization helpers for multi-source lead capture."""

from typing import Any


def parse_whatsapp_message(payload: dict) -> dict[str, Any]:
    return {
        "source": "whatsapp",
        "customer_phone": payload.get("from_number"),
        "message": payload.get("text", ""),
        "details": {},
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
