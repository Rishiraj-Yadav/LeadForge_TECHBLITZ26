"""WhatsApp Cloud API client."""

import httpx
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

BASE_URL = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"


class WhatsAppClient:
    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_text(self, to: str, text: str) -> dict:
        """Send a text message via WhatsApp."""
        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            logger.info(f"WhatsApp message sent to {to}")
            return resp.json()

    async def send_interactive_buttons(
        self, to: str, body_text: str, buttons: list[dict]
    ) -> dict:
        """Send an interactive button message (max 3 buttons)."""
        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": btn["id"], "title": btn["title"]},
                        }
                        for btn in buttons[:3]
                    ]
                },
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            logger.info(f"WhatsApp interactive message sent to {to}")
            return resp.json()

    async def send_template(self, to: str, template_name: str, params: list[str]) -> dict:
        """Send a pre-approved template message."""
        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": p} for p in params
                        ],
                    }
                ],
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            return resp.json()

    async def mark_read(self, message_id: str) -> dict:
        """Mark a message as read."""
        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=self.headers, timeout=30)
            return resp.json()


def get_whatsapp_client() -> WhatsAppClient:
    return WhatsAppClient()
