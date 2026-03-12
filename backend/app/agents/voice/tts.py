"""ElevenLabs text-to-speech adapter."""

from elevenlabs.client import ElevenLabs

from app.config import get_settings

settings = get_settings()


class TTSService:
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    def synthesize(self, text: str) -> bytes:
        return self.client.text_to_speech.convert(
            voice_id=settings.ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            text=text,
        )
