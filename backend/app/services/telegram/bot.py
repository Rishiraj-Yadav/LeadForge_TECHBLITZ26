"""Telegram Bot API client for customer conversations and rep notifications."""

import httpx
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_message(self, chat_id: str, text: str, parse_mode: str | None = None) -> dict:
        """Send a text message."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            logger.info(f"Telegram message sent to {chat_id}")
            return resp.json()

    async def send_inline_keyboard(
        self, chat_id: str, text: str, buttons: list[list[dict]]
    ) -> dict:
        """Send a message with inline keyboard buttons.

        buttons format: [[{"text": "Approve ✅", "callback_data": "approve:lead_123"}]]
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {"inline_keyboard": buttons},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()

    async def edit_message_reply_markup(self, chat_id: str, message_id: int, buttons: list[list[dict]]) -> dict:
        url = f"{self.base_url}/editMessageReplyMarkup"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": buttons},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()

    async def answer_callback_query(self, callback_query_id: str, text: str = "") -> dict:
        """Acknowledge a button click."""
        url = f"{self.base_url}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id, "text": text}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=30)
            return resp.json()

    async def set_webhook(self, webhook_url: str) -> dict:
        """Register webhook URL with Telegram.

        Call this once during setup:
          POST https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_URL>/api/v1/webhooks/telegram
        """
        url = f"{self.base_url}/setWebhook"
        payload = {"url": webhook_url}
        if settings.TELEGRAM_WEBHOOK_SECRET:
            payload["secret_token"] = settings.TELEGRAM_WEBHOOK_SECRET
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()

    def parse_webhook(self, payload: dict) -> dict:
        """Parse incoming Telegram webhook update."""
        result = {"type": None, "chat_id": None, "text": "", "username": "", "from_name": ""}

        if payload.get("callback_query"):
            cb = payload["callback_query"]
            result["type"] = "callback"
            result["chat_id"] = cb["message"]["chat"]["id"]
            result["text"] = cb.get("data", "")
            result["callback_query_id"] = cb["id"]
            result["username"] = cb.get("from", {}).get("username", "")
            result["from_name"] = cb.get("from", {}).get("first_name", "")
            result["message_id"] = cb.get("message", {}).get("message_id")
        elif payload.get("message"):
            msg = payload["message"]
            result["type"] = "message"
            result["chat_id"] = msg["chat"]["id"]
            result["text"] = msg.get("text", "")
            result["username"] = msg.get("from", {}).get("username", "")
            result["from_name"] = msg.get("from", {}).get("first_name", "")
            result["message_id"] = msg.get("message_id")

        return result


def get_telegram_bot() -> TelegramBot:
    return TelegramBot()
