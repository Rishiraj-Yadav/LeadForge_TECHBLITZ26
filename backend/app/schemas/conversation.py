"""Conversation & Message schemas."""

from datetime import datetime
from pydantic import BaseModel
from typing import Any


class MessageCreate(BaseModel):
    role: str
    content: str
    channel: str
    msg_metadata: dict[str, Any] = {}


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    channel: str
    msg_metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    lead_id: str
    channel: str
    intent: str | None
    sentiment: float
    last_activity: datetime | None
    next_followup: datetime | None
    messages: list[MessageResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
