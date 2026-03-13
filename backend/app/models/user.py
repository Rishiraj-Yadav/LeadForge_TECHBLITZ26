"""User model — sales reps / admins."""

from typing import Optional
from beanie import Document, PydanticObjectId

from app.models.base import TimestampMixin


class User(TimestampMixin, Document):
    business_id: PydanticObjectId
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    role: str = "rep"                          # admin, rep
    phone: Optional[str] = None
    is_active: bool = True

    # Notification preferences
    telegram_chat_id: Optional[str] = None
    preferred_notification: str = "telegram"   # telegram, email

    class Settings:
        name = "users"
