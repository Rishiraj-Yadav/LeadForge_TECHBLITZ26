"""Conversation model — tracks ongoing dialogues per lead."""

from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    channel = Column(String(20), nullable=False)  # whatsapp, instagram, email, voice
    intent = Column(String(50))  # inquiry, qualification, objection, ready_to_buy
    sentiment = Column(Float, default=0.5)
    last_activity = Column(DateTime(timezone=True))
    next_followup = Column(DateTime(timezone=True))

    # Relationships
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", lazy="selectin",
                            order_by="Message.created_at")
