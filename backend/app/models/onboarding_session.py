"""Onboarding session — temporary state for Telegram owner setup wizard."""

from datetime import datetime, timezone
from typing import Optional
from beanie import Document
from pydantic import Field


class OnboardingSession(Document):
    """Tracks a business owner's in-progress Telegram onboarding conversation."""

    telegram_chat_id: str
    step: str = "name"
    data: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    "questions",
    "welcome_message",
]

WIZARD_QUESTIONS = {
    "name": (
        "👋 Welcome to *LeadForge Setup Wizard*!\n\n"
        "Let's set up your business in a few quick steps.\n\n"
        "*Step 1/8* — What is your business name?"
    ),
    "industry": (
        "✅ Got it!\n\n"
        "*Step 2/8* — What industry are you in?\n\n"
        "Reply with one of:\n"
        "• restaurant\n"
        "• hotel\n"
        "• real estate\n"
        "• other"
    ),
    "phone": (
        "✅ Perfect!\n\n"
        "*Step 3/8* — What is your business phone number?\n"
        "(Type 'skip' to skip)"
    ),
    "email": (
        "✅ Noted!\n\n"
        "*Step 4/8* — What is your business email?\n"
        "(Type 'skip' to skip)"
    ),
    "business_hours": (
        "✅ Got it!\n\n"
        "*Step 5/8* — What are your business hours?\n"
        "Example: Mon-Sat 9AM-10PM\n"
        "(Type 'skip' to skip)"
    ),
    "services": (
        "✅ Great!\n\n"
        "*Step 6/8* — Briefly describe your services or products:\n"
        "(This helps the AI answer customer questions accurately)"
    ),
    "questions": (
        "✅ Now the important step!\n\n"
        "*Step 7/8* — Enter 5 questions your AI should ask customers during enquiry.\n\n"
        "Send them all at once, one per line. Example:\n\n"
        "How many guests?\n"
        "What date and time?\n"
        "Any dietary restrictions?\n"
        "What is your budget?\n"
        "What is the occasion?"
    ),
    "welcome_message": (
        "✅ Almost done!\n\n"
        "*Step 8/8* — What welcome message should customers see when they first chat?\n"
        "Example: Hi! Welcome to Bella Vista. How can I help you today?"
    ),
}
