"""WhatsApp webhook verification + message parsing."""

from app.config import get_settings
from app.schemas.webhook import WhatsAppMessage

settings = get_settings()


def verify_webhook(mode: str, token: str, challenge: str) -> str | None:
    """Verify webhook subscription from Meta.
    Returns the challenge string if valid, None otherwise.
    """
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return challenge
    return None


def parse_webhook_payload(payload: dict) -> list[WhatsAppMessage]:
    """Extract messages from a WhatsApp webhook payload."""
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                parsed = WhatsAppMessage(
                    from_number=msg.get("from", ""),
                    message_id=msg.get("id", ""),
                    timestamp=msg.get("timestamp", ""),
                    type=msg.get("type", "text"),
                )
                if msg.get("type") == "text":
                    parsed.text = msg.get("text", {}).get("body", "")
                elif msg.get("type") == "interactive":
                    reply = msg.get("interactive", {}).get("button_reply", {})
                    parsed.button_reply_id = reply.get("id")
                    parsed.button_reply_title = reply.get("title")
                    parsed.text = reply.get("title", "")
                messages.append(parsed)
    return messages
