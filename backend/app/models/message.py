"""Message model — individual messages in a conversation."""

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models.base import TimestampMixin


class Message(TimestampMixin, Document):
    conversation_id: PydanticObjectId
    role: str                                  # customer, ai, rep
    content: str
    channel: str                               # telegram, instagram, email, voice
    msg_metadata: dict = Field(default_factory=dict)

    class Settings:
        name = "messages"
