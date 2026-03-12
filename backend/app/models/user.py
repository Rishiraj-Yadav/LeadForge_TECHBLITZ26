"""User model — sales reps / admins."""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(20), default="rep")  # admin, rep
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)

    # Notification preferences
    whatsapp_number = Column(String(20))
    telegram_chat_id = Column(String(50))
    preferred_notification = Column(String(20), default="whatsapp")  # whatsapp, telegram

    # Relationships
    business = relationship("Business", back_populates="users")
