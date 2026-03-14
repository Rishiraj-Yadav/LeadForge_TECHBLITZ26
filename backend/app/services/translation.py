"""Translation service — uses Google Gemini for reliable real-time translation.

Lingo.dev is kept as an optional fallback (set LINGODOTDEV_API_KEY to enable it).
If neither works, the original text is returned unchanged so the system never breaks.
"""

from __future__ import annotations

import httpx
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Supported languages (English, Hindi, Marathi)
SUPPORTED_LANGUAGES = {
    "en": "English 🇬🇧",
    "hi": "हिन्दी 🇮🇳",
    "mr": "मराठी 🇮🇳",
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
}

# Lingo.dev API (optional fallback)
LINGO_API_URL = "https://engine.lingo.dev/translate"


class TranslationService:
    """Translate text using Google Gemini (primary) or lingo.dev (fallback)."""

    def __init__(self):
        self.lingo_key = settings.LINGODOTDEV_API_KEY
        self.google_key = settings.GOOGLE_API_KEY

    async def translate(
        self,
        text: str,
        target_locale: str,
        source_locale: str = "en",
    ) -> str:
        """Translate text. Returns original text on any failure."""
        if target_locale == source_locale:
            return text

        if not text or not text.strip():
            return text

        # Try Gemini first (most reliable since it's already configured)
        result = await self._translate_with_gemini(text, target_locale, source_locale)
        if result and result != text:
            return result

        # Fallback: try lingo.dev if key is set
        if self.lingo_key:
            result = await self._translate_with_lingo(text, target_locale, source_locale)
            if result and result != text:
                return result

        logger.warning(f"All translation methods failed for [{source_locale}→{target_locale}], using original")
        return text

    async def _translate_with_gemini(
        self,
        text: str,
        target_locale: str,
        source_locale: str,
    ) -> str:
        """Use Gemini to translate text via a direct API call."""
        if not self.google_key:
            return text

        target_lang = LANGUAGE_NAMES.get(target_locale, target_locale)
        source_lang = LANGUAGE_NAMES.get(source_locale, source_locale)

        prompt = (
            f"Translate the following text from {source_lang} to {target_lang}.\n"
            f"Rules:\n"
            f"- Return ONLY the translated text — no explanations, no quotes, no extra text\n"
            f"- Preserve line breaks and formatting\n"
            f"- If the text is already in {target_lang}, return it unchanged\n\n"
            f"Text to translate:\n{text}"
        )

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            translated = parts[0].get("text", "").strip()
                            if translated:
                                logger.info(f"Gemini translated [{source_locale}→{target_locale}]: {text[:40]!r}")
                                return translated
                else:
                    logger.error(f"Gemini translation API error {resp.status_code}: {resp.text[:200]}")
        except Exception as exc:
            logger.error(f"Gemini translation exception: {exc}")

        return text

    async def _translate_with_lingo(
        self,
        text: str,
        target_locale: str,
        source_locale: str,
    ) -> str:
        """Try lingo.dev as fallback translation service."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    LINGO_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.lingo_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "sourceLocale": source_locale,
                        "targetLocale": target_locale,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, str):
                        return data
                    translated = (
                        data.get("translatedText")
                        or data.get("translation")
                        or data.get("text")
                        or data.get("result")
                    )
                    if translated:
                        return translated
                else:
                    logger.error(f"Lingo.dev error {resp.status_code}: {resp.text[:200]}")
        except Exception as exc:
            logger.error(f"Lingo.dev translation exception: {exc}")

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
