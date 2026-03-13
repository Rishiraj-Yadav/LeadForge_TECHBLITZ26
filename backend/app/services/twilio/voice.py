"""Twilio voice call handling."""

from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Gather, Connect, Stream
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class VoiceService:
    def __init__(self):
        self.client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone = settings.TWILIO_PHONE_NUMBER

    def create_inbound_twiml(self, websocket_url: str) -> str:
        """Generate TwiML to stream inbound call audio to our WebSocket for AI processing."""
        response = VoiceResponse()
        response.say("Welcome to LeadForge. Please tell us how we can help you.", voice="alice")
        connect = Connect()
        stream = Stream(url=websocket_url)
        connect.append(stream)
        response.append(connect)
        return str(response)

    def create_gather_twiml(self, prompt: str, action_url: str) -> str:
        """Generate TwiML that speaks a prompt and gathers speech input."""
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action=action_url,
            method="POST",
            speech_timeout="auto",
            language="en-US",
        )
        gather.say(prompt, voice="alice")
        response.append(gather)
        # If no input, repeat
        response.redirect(action_url)
        return str(response)

    async def make_outbound_call(self, to: str, twiml_url: str) -> str:
        """Initiate an outbound call. Returns call SID."""
        call = self.client.calls.create(
            to=to,
            from_=self.phone,
            url=twiml_url,
        )
        logger.info(f"Outbound call initiated: {call.sid} to {to}")
        return call.sid

    def transfer_to_rep(self, rep_phone: str) -> str:
        """Generate TwiML to transfer the call to a human rep."""
        response = VoiceResponse()
        response.say("Let me connect you with a team member.", voice="alice")
        response.dial(rep_phone)
        return str(response)


def get_voice_service() -> VoiceService:
    return VoiceService()
