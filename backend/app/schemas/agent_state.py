"""LangGraph agent state schemas."""

from __future__ import annotations
from typing import Any, TypedDict, Annotated
from langgraph.graph.message import add_messages


class LeadData(TypedDict, total=False):
    """Structured lead object passed between agents."""
    id: str
    business_id: str
    source: str
    customer_name: str
    customer_phone: str
    customer_email: str
    message: str
    details: dict[str, Any]
    conversation_history: list[dict[str, str]]


class ResearchResult(TypedDict, total=False):
    legitimacy_score: float
    company_info: dict[str, Any]
    social_profiles: list[str]
    domain_age: str
    summary: str


class ScoreResult(TypedDict, total=False):
    score: float
    reasoning: str
    urgency: str
    budget_indicators: list[str]


class AgentState(TypedDict, total=False):
    """The master state flowing through the LangGraph orchestrator."""
    # Core data
    lead: LeadData
    research: ResearchResult
    scoring: ScoreResult

    # Decisions
    rep_decision: str           # pending, approved, rejected
    current_agent: str          # which agent is active
    next_agent: str             # routing target

    # Conversation
    messages: Annotated[list, add_messages]
    intent: str                 # inquiry, qualification, objection, ready_to_buy
    sentiment: float

    # Pipeline
    stage: str                  # new, contacted, qualified, proposal, negotiation, won, lost

    # Control flow
    error: str | None
    should_escalate: bool
    follow_up_scheduled: bool
