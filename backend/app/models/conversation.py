"""Conversation model — tracks ongoing dialogues per lead."""

from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId

from app.models.base import TimestampMixin


class Conversation(TimestampMixin, Document):
    lead_id: PydanticObjectId
    channel: str                              # telegram, instagram, email, voice
    intent: Optional[str] = None              # inquiry, qualification, objection, ready_to_buy
    sentiment: float = 0.5
    last_activity: Optional[datetime] = None
    next_followup: Optional[datetime] = None

    class Settings:
        name = "conversations"
