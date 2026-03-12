"""Conversation & Message schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Any


class MessageCreate(BaseModel):
    role: str
    content: str
    channel: str
    metadata_: dict[str, Any] = {}


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    channel: str
    metadata_: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: UUID
    lead_id: UUID
    channel: str
    intent: str | None
    sentiment: float
    last_activity: datetime | None
    next_followup: datetime | None
    messages: list[MessageResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
