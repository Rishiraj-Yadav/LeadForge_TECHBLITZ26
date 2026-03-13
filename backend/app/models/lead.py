"""Lead model — core entity."""

import enum
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models.base import TimestampMixin


class LeadSource(str, enum.Enum):
    INSTAGRAM = "instagram"
    EMAIL = "email"
    VOICE = "voice"
    FORM = "form"
    TELEGRAM = "telegram"
    MANUAL = "manual"


class LeadStage(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class RepDecision(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Lead(TimestampMixin, Document):
    business_id: PydanticObjectId
    source: LeadSource

    # Customer info
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None

    # Dynamic details (industry-specific)
    details: dict = Field(default_factory=dict)

    # Scoring
    score: float = 0.0
    score_reasoning: Optional[str] = None

    # Research
    research_data: dict = Field(default_factory=dict)

    # Pipeline
    stage: LeadStage = LeadStage.NEW
    rep_decision: RepDecision = RepDecision.PENDING

    class Settings:
        name = "leads"
