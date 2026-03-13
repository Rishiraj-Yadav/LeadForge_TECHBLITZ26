"""Webhook payload schemas."""

from pydantic import BaseModel
from typing import Any


# ── Instagram Webhook ──
class InstagramMessage(BaseModel):
    sender_id: str = ""
    message_text: str = ""
    timestamp: str = ""


class InstagramWebhookPayload(BaseModel):
    object: str = ""
    entry: list[dict[str, Any]] = []


# ── Telegram Webhook ──
class TelegramMessage(BaseModel):
    chat_id: int = 0
    text: str = ""
    from_username: str = ""
    from_name: str = ""
    message_id: int = 0
    callback_data: str | None = None
    callback_query_id: str | None = None


class TelegramWebhookPayload(BaseModel):
    update_id: int = 0
    message: dict[str, Any] | None = None
    callback_query: dict[str, Any] | None = None


# ── Form Submission ──
class FormSubmission(BaseModel):
    business_id: str
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    message: str = ""
    source_url: str | None = None
