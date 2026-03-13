"""Unified communication dispatcher for Telegram, Instagram, email, and SMS backup."""

from app.services.email.sendgrid import get_email_service
from app.services.instagram.client import get_instagram_client
from app.services.telegram.bot import get_telegram_bot
from app.services.twilio.sms import get_sms_service


class CommunicationService:
    async def send_customer_message(self, lead: dict, text: str) -> dict:
        source = lead.get("source")
        details = lead.get("details", {})

        if source == "telegram" and details.get("telegram_chat_id"):
            result = await get_telegram_bot().send_message(str(details["telegram_chat_id"]), text)
            return {"channel": "telegram", "result": result}

        if source == "instagram" and details.get("instagram_sender_id"):
            result = await get_instagram_client().send_message(details["instagram_sender_id"], text)
            return {"channel": "instagram", "result": result}

        if source == "email" and lead.get("customer_email"):
            status = await get_email_service().send_email(
                lead["customer_email"],
                "LeadForge follow-up",
                f"<p>{text}</p>",
            )
            return {"channel": "email", "result": status}

        if lead.get("customer_phone"):
            sid = await get_sms_service().send_sms(lead["customer_phone"], text)
            return {"channel": "sms", "result": sid}

        return {"channel": "none", "result": None}

    async def notify_rep(self, text: str, buttons: list[list[dict]] | None = None) -> dict:
        bot = get_telegram_bot()
        if buttons:
            result = await bot.send_inline_keyboard(bot_chat_id(), text, buttons)
        else:
            result = await bot.send_message(bot_chat_id(), text)
        return {"channel": "telegram", "result": result}


def bot_chat_id() -> str:
    from app.config import get_settings

    return get_settings().REP_TELEGRAM_CHAT_ID


def get_communication_service() -> CommunicationService:
    return CommunicationService()