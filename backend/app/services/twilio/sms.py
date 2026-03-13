"""Twilio SMS service."""

from twilio.rest import Client as TwilioClient
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SMSService:
    def __init__(self):
        self.client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone = settings.TWILIO_PHONE_NUMBER

    async def send_sms(self, to: str, body: str) -> str:
        """Send an SMS. Returns message SID."""
        message = self.client.messages.create(
            to=to,
            from_=self.phone,
            body=body,
        )
        logger.info(f"SMS sent to {to}: {message.sid}")
        return message.sid


def get_sms_service() -> SMSService:
    return SMSService()
