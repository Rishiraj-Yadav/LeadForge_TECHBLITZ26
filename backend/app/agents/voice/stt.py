"""Deepgram speech-to-text adapter."""

from deepgram import DeepgramClient

from app.config import get_settings

settings = get_settings()


class STTService:
    def __init__(self):
        self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)

    async def transcribe_url(self, audio_url: str) -> str:
        response = await self.client.listen.asyncrest.v("1").transcribe_url(
            {"url": audio_url},
            {"smart_format": True, "model": "nova-2"},
        )
        return response["results"]["channels"][0]["alternatives"][0]["transcript"]
