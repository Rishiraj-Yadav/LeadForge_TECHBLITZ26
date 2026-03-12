"""Lead Pydantic schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Any


class CustomerInfo(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None


class LeadCreate(BaseModel):
    business_id: UUID
    source: str
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class LeadUpdate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    details: dict[str, Any] | None = None
    score: float | None = None
    score_reasoning: str | None = None
    stage: str | None = None
    rep_decision: str | None = None


class LeadResponse(BaseModel):
    id: UUID
    business_id: UUID
    source: str
    customer_name: str | None
    customer_phone: str | None
    customer_email: str | None
    details: dict[str, Any]
    score: float
    score_reasoning: str | None
    research_data: dict[str, Any]
    stage: str
    rep_decision: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadSummary(BaseModel):
    id: UUID
    source: str
    customer_name: str | None
    score: float
    stage: str
    rep_decision: str
    created_at: datetime

    model_config = {"from_attributes": True}
