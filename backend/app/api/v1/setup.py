
"""Setup endpoints for configuring external service integrations."""

import asyncio
from fastapi import APIRouter, Query

from app.config import get_settings
from app.services.telegram.bot import get_telegram_bot
from app.core.logging import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.post("/telegram-webhook")
async def register_telegram_webhook(
    webhook_url: str = Query(
        default=None,
        description="Full public URL for the Telegram webhook. "
        "Defaults to API_BASE_URL/api/v1/webhooks/telegram.",
    ),
):
    """Register the Telegram webhook so the bot receives updates."""
    url = webhook_url or f"{settings.API_BASE_URL}/api/v1/webhooks/telegram"
    bot = get_telegram_bot()
    
    try:
        result = await asyncio.wait_for(bot.set_webhook(url), timeout=5.0)
        logger.info(f"Telegram webhook registered: {url} -> {result}")
        return {
            "status": "ok", 
            "webhook_url": url, 
            "telegram_response": result
        }
    except asyncio.TimeoutError:
        logger.error(f"Telegram webhook registration timed out: {url}")
        return {
            "status": "timeout",
            "webhook_url": url,
            "error": "Request to Telegram API timed out after 5 seconds"
        }
    except Exception as exc:
        logger.error(f"Telegram webhook registration failed: {exc}")
        return {
            "status": "error",
            "webhook_url": url,
            "error": str(exc)
        }


async def auto_register_telegram_webhook():
    """Best-effort webhook registration on startup with timeout."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping webhook registration")
        return
    
    if not settings.API_BASE_URL:
        logger.warning("API_BASE_URL not set, skipping webhook registration")
        return
        
    try:
        url = f"{settings.API_BASE_URL}/api/v1/webhooks/telegram"
        bot = get_telegram_bot()
        
        # Set 3-second timeout for startup webhook registration
        result = await asyncio.wait_for(bot.set_webhook(url), timeout=3.0)
        logger.info(f"✅ Auto-registered Telegram webhook: {url}")
        logger.debug(f"Telegram response: {result}")
        
    except asyncio.TimeoutError:
        logger.warning(
            f"⏱️  Telegram webhook registration timed out (3s). "
            f"This is OK - you can register it manually later."
        )
    except Exception as exc:
        logger.warning(
            f"⚠️  Failed to auto-register Telegram webhook: {exc}. "
            f"This is OK - you can register it manually at POST /api/v1/setup/telegram-webhook"
        )