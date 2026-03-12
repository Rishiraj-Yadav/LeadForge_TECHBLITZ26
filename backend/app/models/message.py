"""Message model — individual messages in a conversation."""

from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)     # customer, ai, rep
    content = Column(Text, nullable=False)
    channel = Column(String(20), nullable=False)   # whatsapp, instagram, email, voice
    metadata_ = Column("metadata", JSON, default=dict)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
