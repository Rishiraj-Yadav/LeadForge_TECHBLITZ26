"""Business / tenant model."""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Business(BaseModel):
    __tablename__ = "businesses"

    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    website = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    is_active = Column(Boolean, default=True)

    # WhatsApp / Telegram config
    whatsapp_number = Column(String(20))
    telegram_chat_id = Column(String(50))

    # Relationships
    leads = relationship("Lead", back_populates="business", lazy="selectin")
    users = relationship("User", back_populates="business", lazy="selectin")
