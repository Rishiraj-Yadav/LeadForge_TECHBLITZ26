"""Onboarding session — temporary state for Telegram owner setup wizard."""

from datetime import datetime, timezone
from typing import Optional
from beanie import Document


class OnboardingSession(Document):
    """Tracks a business owner's in-progress Telegram onboarding conversation."""

    telegram_chat_id: str          # owner's Telegram chat ID (unique per session)
    step: str                      # current wizard step
    data: dict = {}                # collected answers so far

    created_at: datetime = None

    def __init__(self, **kwargs):
        if "created_at" not in kwargs:
            kwargs["created_at"] = datetime.now(timezone.utc)
        super().__init__(**kwargs)

    class Settings:
        name = "onboarding_sessions"


# Ordered wizard steps
WIZARD_STEPS = [
    "name",
    "industry",
    "phone",
    "email",
    "business_hours",
    "services",
    "welcome_message",
]

WIZARD_QUESTIONS = {
    "name": "👋 Welcome to *LeadForge Setup Wizard*!\n\nLet's set up your business in a few quick steps.\n\n*Step 1/7* — What is your *business name*?",
    "industry": "✅ Got it!\n\n*Step 2/7* — What *industry* are you in?\n\nReply with one of:\n• `restaurant`\n• `hotel`\n• `real_estate`\n• `other`",
    "phone": "✅ Perfect!\n\n*Step 3/7* — What is your *business phone number*?\n(Type `skip` to skip)",
    "email": "✅ Noted!\n\n*Step 4/7* — What is your *business email*?\n(Type `skip` to skip)",
    "business_hours": "✅ Got it!\n\n*Step 5/7* — What are your *business hours*?\nExample: `Mon-Sat 9AM-10PM`\n(Type `skip` to skip)",
    "services": "✅ Great!\n\n*Step 6/7* — Briefly describe your *services or products*:\n(This helps the AI answer customer questions accurately)",
    "welcome_message": "✅ Almost done!\n\n*Step 7/7* — What *welcome message* should customers see when they first chat with your AI?\nExample: `Hi! Welcome to Bella Vista. How can I help you today?`",
}
