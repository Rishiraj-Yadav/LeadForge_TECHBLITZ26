"""Instagram Graph API client for DM handling."""

import httpx
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

BASE_URL = "https://graph.facebook.com/v21.0"


class InstagramClient:
    def __init__(self):
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.account_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID

    async def send_message(self, recipient_id: str, text: str) -> dict:
        """Send a DM reply to an Instagram user."""
        url = f"{BASE_URL}/me/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
        }
        params = {"access_token": self.access_token}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, params=params, timeout=30)
            resp.raise_for_status()
            logger.info(f"Instagram DM sent to {recipient_id}")
            return resp.json()

    def parse_webhook(self, payload: dict) -> list[dict]:
        """Parse Instagram messaging webhook."""
        messages = []
        for entry in payload.get("entry", []):
            for messaging in entry.get("messaging", []):
                sender_id = messaging.get("sender", {}).get("id", "")
                message = messaging.get("message", {})
                if message and sender_id != self.account_id:
                    messages.append({
                        "sender_id": sender_id,
                        "text": message.get("text", ""),
                        "timestamp": messaging.get("timestamp", ""),
                        "message_id": message.get("mid", ""),
                    })
        return messages


def get_instagram_client() -> InstagramClient:
    return InstagramClient()
