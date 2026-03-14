"""Translation service using lingo.dev SDK for multi-language support."""

from __future__ import annotations

import httpx
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Language codes and display names (English, Hindi, Marathi)
SUPPORTED_LANGUAGES = {
    "en": "English 🇬🇧",
    "hi": "हिन्दी 🇮🇳",
    "mr": "मराठी 🇮🇳",
}

# Lingo.dev API base URL
LINGO_API_URL = "https://engine.lingo.dev/translate"


class TranslationService:
    """Translate text using lingo.dev REST API."""

    def __init__(self):
        self.api_key = settings.LINGODOTDEV_API_KEY
        self.enabled = bool(self.api_key)

    async def translate(
        self,
        text: str,
        target_locale: str,
        source_locale: str = "en",
    ) -> str:
        """Translate text from source locale to target locale.

        Falls back to original text if translation fails or target is same as source.
        """
        if not self.enabled:
            logger.warning("Lingo.dev API key not set — skipping translation")
            return text

        if target_locale == source_locale:
            return text

        if not text or not text.strip():
            return text

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    LINGO_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "sourceLocale": source_locale,
                        "targetLocale": target_locale,
                    },
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    translated = data.get("translatedText") or data.get("text") or data.get("result")
                    if translated:
                        return translated
                    # Try other response shapes
                    if isinstance(data, str):
                        return data
                    return text
                else:
                    logger.error(f"Lingo.dev API error {resp.status_code}: {resp.text}")
                    return text
        except Exception as exc:
            logger.error(f"Translation failed: {exc}")
            return text

    async def translate_to_english(self, text: str, source_locale: str) -> str:
        """Translate customer message to English for AI processing."""
        return await self.translate(text, target_locale="en", source_locale=source_locale)

    async def translate_from_english(self, text: str, target_locale: str) -> str:
        """Translate AI response from English to customer's language."""
        return await self.translate(text, target_locale=target_locale, source_locale="en")


_service: TranslationService | None = None


def get_translation_service() -> TranslationService:
    global _service
    if _service is None:
        _service = TranslationService()
    return _service
