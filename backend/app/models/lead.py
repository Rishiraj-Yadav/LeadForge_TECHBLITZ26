"""Lead model — core entity."""

from sqlalchemy import Column, String, Float, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class LeadSource(str, enum.Enum):
    WHATSAPP = "whatsapp"
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


class Lead(BaseModel):
    __tablename__ = "leads"

    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    source = Column(SAEnum(LeadSource), nullable=False)

    # Customer info
    customer_name = Column(String(255))
    customer_phone = Column(String(20))
    customer_email = Column(String(255))

    # Dynamic details (industry-specific)
    details = Column(JSON, default=dict)

    # Scoring
    score = Column(Float, default=0.0)
    score_reasoning = Column(Text)

    # Research
    research_data = Column(JSON, default=dict)

    # Pipeline
    stage = Column(SAEnum(LeadStage), default=LeadStage.NEW)
    rep_decision = Column(SAEnum(RepDecision), default=RepDecision.PENDING)

    # Relationships
    business = relationship("Business", back_populates="leads")
    conversations = relationship("Conversation", back_populates="lead", lazy="selectin")
