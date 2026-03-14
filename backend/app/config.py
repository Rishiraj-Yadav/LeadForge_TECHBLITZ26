"""LeadForge configuration — loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # ── App ──
    APP_NAME: str = "LeadForge"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"
    API_BASE_URL: str = "http://localhost:8005"

    # ── MongoDB ──
    MONGODB_URL: str = ""

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Gemini ──
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"

    # ── Instagram ──
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = ""

    # ── Telegram ──
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""  # e.g., "LeadForgeBot" — for t.me/BOT?start=CODE
    TELEGRAM_WEBHOOK_SECRET: str = ""
    REP_TELEGRAM_CHAT_ID: str = ""

    # ── Twilio ──
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # ── Deepgram ──
    DEEPGRAM_API_KEY: str = ""

    # ── ElevenLabs ──
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # ── SendGrid ──
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""
    SENDGRID_FROM_NAME: str = "LeadForge"

    # ── Serper ──
    SERPER_API_KEY: str = ""

    # ── Lingo.dev (Translation) ──
    LINGODOTDEV_API_KEY: str = ""

    # ── Pinecone ──
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "leadforge-conversations"
    PINECONE_ENVIRONMENT: str = "us-east-1"

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[1] / ".env"),
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
