"""Business / tenant model."""

from typing import Optional
from beanie import Document, Indexed
from pydantic import Field

from app.models.base import TimestampMixin


class Business(TimestampMixin, Document):
    name: str
    industry: Optional[str] = None          # restaurant, hotel, real_estate, other
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True

    # Onboarding
    business_hours: Optional[str] = None          # e.g., "Mon-Sat 9AM-10PM"
    services_offered: Optional[str] = None        # description of services/products
    capture_fields: dict = Field(default_factory=dict)  # {"guest_count": true, ...}
    capture_questions: list = Field(default_factory=list)  # owner-defined questions for AI
    onboarding_complete: bool = False
    welcome_message: Optional[str] = None         # custom greeting for customers

    # Telegram config
    telegram_bot_username: Optional[str] = None
    telegram_chat_id: Optional[str] = None        # owner's chat ID for notifications
    deep_link_code: Optional[Indexed(str, unique=True)] = None  # t.me/bot?start=CODE

    class Settings:
        name = "businesses"
