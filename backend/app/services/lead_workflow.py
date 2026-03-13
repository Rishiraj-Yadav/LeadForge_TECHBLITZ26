"""Persistence and workflow helpers for lead communication flows.

Two-phase processing:
  Phase 1 (Capture) — every message:  Gemini AI has natural conversation, extracts info
  Phase 2 (Pipeline) — once capture is complete: Research → Scoring → Notification
"""

from __future__ import annotations

from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.agents.orchestrator import run_lead_workflow
from app.agents.outreach.agent import OutreachAgent
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.lead import Lead, LeadStage, RepDecision
from app.models.message import Message
from app.services.communication import get_communication_service
from app.services.gemini_capture import get_capture_service
from app.core.logging import get_logger
from app.utils.industry import infer_details_from_message

logger = get_logger(__name__)


def _safe_oid(value: str | None) -> PydanticObjectId | None:
    if not value:
        return None
    try:
        return PydanticObjectId(str(value))
    except Exception:
        return None


async def resolve_business_id(business_id: str | None) -> PydanticObjectId:
    parsed = _safe_oid(business_id)
    if parsed:
        existing = await Business.get(parsed)
        if existing:
            return existing.id

    # Fallback: use first business
    business = await Business.find_one(sort="created_at")
    if business:
        return business.id

    # Create default business
    business = Business(
        name="LeadForge Default Business",
        industry="generic",
        is_active=True,
    )
    await business.insert()
    return business.id


async def get_or_create_lead_for_channel(
    *,
    source: str,
    business_id: str | None,
    customer_name: str | None,
    customer_phone: str | None,
    customer_email: str | None,
    details: dict,
    message_text: str,
) -> Lead:
    chat_id = details.get("telegram_chat_id")

    existing = None
    if source == "telegram" and chat_id:
        # Use raw MongoDB query for nested dict field lookup
        existing = await Lead.find_one(
            {
                "source": "telegram",
                "details.telegram_chat_id": str(chat_id),
                "stage": {"$nin": [LeadStage.WON.value, LeadStage.LOST.value]},
            }
        )

    if existing:
        existing.customer_name = customer_name or existing.customer_name
        existing.customer_phone = customer_phone or existing.customer_phone
        existing.customer_email = customer_email or existing.customer_email
        existing.details = infer_details_from_message(message_text, {**(existing.details or {}), **details})
        await existing.save()
        return existing

    lead = Lead(
        business_id=await resolve_business_id(business_id),
        source=source,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        details=infer_details_from_message(message_text, details),
        rep_decision=RepDecision.PENDING,
    )
    await lead.insert()
    return lead


async def get_or_create_conversation(lead_id: PydanticObjectId, channel: str) -> Conversation:
    conversation = await Conversation.find_one(
        {"lead_id": lead_id, "channel": channel}
    )
    if conversation:
        return conversation

    conversation = Conversation(
        lead_id=lead_id,
        channel=channel,
        last_activity=datetime.now(timezone.utc),
    )
    await conversation.insert()
    return conversation


async def append_message(
    conversation_id: PydanticObjectId,
    *,
    role: str,
    channel: str,
    content: str,
    msg_metadata: dict | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        channel=channel,
        content=content,
        msg_metadata=msg_metadata or {},
    )
    await message.insert()
    return message


async def _load_conversation_history(conversation_id: PydanticObjectId) -> list[dict]:
    """Load all messages in a conversation for Gemini context."""
    messages = await Message.find(
        {"conversation_id": conversation_id}
    ).sort("created_at").to_list()
    return [{"role": m.role, "content": m.content} for m in messages]


async def _load_business(business_id) -> Business | None:
    try:
        return await Business.get(business_id)
    except Exception:
        return None


async def process_customer_message(
    *,
    source: str,
    business_id: str | None,
    customer_name: str | None,
    customer_phone: str | None,
    customer_email: str | None,
    details: dict,
    message_text: str,
) -> dict:
    """Two-phase lead processing:
    Phase 1 — Conversational capture (every message)
    Phase 2 — Full pipeline (when capture complete)
    """
    lead = await get_or_create_lead_for_channel(
        source=source,
        business_id=business_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        details=details,
        message_text=message_text,
    )
    conversation = await get_or_create_conversation(lead.id, source)

    # Skip processing for /start command (just a connection, not a real message)
    if message_text == "/start" and details.get("is_start"):
        return {"lead": lead, "conversation": conversation, "state": {}, "sent": []}

    await append_message(conversation.id, role="customer", channel=source, content=message_text)

    # Load business configuration
    business = await _load_business(lead.business_id)
    capture_fields = (business.capture_fields if business else None) or {}

    # If already pipeline-processed (approved/rejected), handle as ongoing conversation
    if lead.rep_decision in (RepDecision.APPROVED, RepDecision.REJECTED):
        return await _handle_ongoing_conversation(lead, conversation, source, message_text, business)

    # ── PHASE 1: Gemini conversational capture ──
    if capture_fields:
        history = await _load_conversation_history(conversation.id)
        capture_service = get_capture_service()

        captured_so_far = {
            k: v for k, v in (lead.details or {}).items()
            if k in capture_fields
        }

        try:
            result = await capture_service.process_message(
                message_text,
                business_name=business.name if business else "Our Business",
                business_industry=business.industry if business else "general",
                services_offered=business.services_offered if business else None,
                capture_fields=capture_fields,
                captured_so_far=captured_so_far,
                conversation_history=history,
            )
        except Exception as exc:
            logger.error(f"Gemini capture failed: {exc}")
            result = {
                "reply": "Thanks for your message! Let me help you with that.",
                "extracted_fields": {},
                "capture_complete": False,
            }

        # Update lead details with newly extracted fields
        updated_details = dict(lead.details or {})
        updated_details.update(result["extracted_fields"])
        lead.details = updated_details

        # Send immediate AI reply
        sent = []
        if result["reply"]:
            dispatcher = get_communication_service()
            send_result = await dispatcher.send_customer_message(
                {
                    "source": source,
                    "customer_phone": lead.customer_phone,
                    "customer_email": lead.customer_email,
                    "details": lead.details or {},
                },
                result["reply"],
            )
            await append_message(
                conversation.id, role="ai", channel=send_result["channel"], content=result["reply"]
            )
            sent.append(send_result)

        # ── PHASE 2: If capture complete, run full pipeline ──
        if result["capture_complete"]:
            return await _run_full_pipeline(lead, conversation, source, message_text, sent)

        conversation.last_activity = datetime.now(timezone.utc)
        await lead.save()
        await conversation.save()
        return {"lead": lead, "conversation": conversation, "state": {}, "sent": sent}

    # No capture fields configured — run full pipeline immediately
    return await _run_full_pipeline(lead, conversation, source, message_text, sent=[])


async def _run_full_pipeline(
    lead: Lead,
    conversation: Conversation,
    source: str,
    message_text: str,
    sent: list[dict],
) -> dict:
    """Phase 2: Run the 9-agent pipeline (Research → Scoring → Notification)."""
    # Load business for notification routing
    business = await _load_business(lead.business_id)
    rep_chat_id = business.telegram_chat_id if business else None

    state = await run_lead_workflow(
        {
            "lead": {
                "id": str(lead.id),
                "business_id": str(lead.business_id),
                "source": source,
                "customer_name": lead.customer_name,
                "customer_phone": lead.customer_phone,
                "customer_email": lead.customer_email,
                "message": message_text,
                "details": lead.details or {},
                "conversation_history": [{"role": "customer", "content": message_text}],
                "business_telegram_chat_id": rep_chat_id,
            }
        }
    )

    scoring = state.get("scoring", {})
    lead.score = scoring.get("score", lead.score)
    lead.score_reasoning = scoring.get("reasoning", lead.score_reasoning)
    lead.research_data = state.get("research", lead.research_data)
    lead.details = {**(lead.details or {}), **state.get("lead", {}).get("details", {})}
    lead.stage = state.get("stage", lead.stage)

    # Write rep_decision BEFORE checking outbound
    if state.get("rep_decision"):
        lead.rep_decision = state["rep_decision"]

    conversation.intent = state.get("intent")
    conversation.sentiment = state.get("sentiment", conversation.sentiment)
    conversation.last_activity = datetime.now(timezone.utc)
    if state.get("next_followup"):
        conversation.next_followup = datetime.fromisoformat(state["next_followup"])

    # Send outbound messages for auto-approved leads
    outbound_messages = []
    for item in state.get("lead", {}).get("conversation_history", []):
        if item.get("role") in {"ai", "ai_followup"}:
            outbound_messages.append(item.get("content", ""))

    if outbound_messages and lead.rep_decision == RepDecision.APPROVED:
        dispatcher = get_communication_service()
        for text in outbound_messages:
            result = await dispatcher.send_customer_message(
                {
                    "source": source,
                    "customer_phone": lead.customer_phone,
                    "customer_email": lead.customer_email,
                    "details": lead.details or {},
                },
                text,
            )
            await append_message(conversation.id, role="ai", channel=result["channel"], content=text)
            sent.append(result)

    await lead.save()
    await conversation.save()

    return {
        "lead": lead,
        "conversation": conversation,
        "state": state,
        "sent": sent,
    }


async def _handle_ongoing_conversation(
    lead: Lead,
    conversation: Conversation,
    source: str,
    message_text: str,
    business: Business | None,
) -> dict:
    """Handle messages from customers whose leads have already been processed."""
    # Use Gemini for ongoing replies too
    history = await _load_conversation_history(conversation.id)
    capture_service = get_capture_service()

    try:
        result = await capture_service.process_message(
            message_text,
            business_name=business.name if business else "Our Business",
            business_industry=business.industry if business else "general",
            services_offered=business.services_offered if business else None,
            capture_fields={},  # No more fields to capture
            captured_so_far=lead.details or {},
            conversation_history=history,
        )
        reply = result["reply"]
    except Exception:
        reply = "Thanks for your message! A team member will follow up with you shortly."

    sent = []
    if reply and lead.rep_decision == RepDecision.APPROVED:
        dispatcher = get_communication_service()
        send_result = await dispatcher.send_customer_message(
            {
                "source": source,
                "customer_phone": lead.customer_phone,
                "customer_email": lead.customer_email,
                "details": lead.details or {},
            },
            reply,
        )
        await append_message(conversation.id, role="ai", channel=send_result["channel"], content=reply)
        sent.append(send_result)

    conversation.last_activity = datetime.now(timezone.utc)
    await conversation.save()
    return {"lead": lead, "conversation": conversation, "state": {}, "sent": sent}


async def apply_rep_decision(lead_id: PydanticObjectId, decision: str) -> tuple[Lead | None, list[dict]]:
    lead = await Lead.get(lead_id)
    if not lead:
        return None, []

    normalized_decision = (decision or "").strip().lower()
    is_approved = normalized_decision in {"approve", "approved"}
    is_rejected = normalized_decision in {"reject", "rejected"}

    if not is_approved and not is_rejected:
        return lead, []

    lead.rep_decision = RepDecision.APPROVED if is_approved else RepDecision.REJECTED
    if is_approved and lead.stage == LeadStage.NEW:
        lead.stage = LeadStage.CONTACTED
    if is_rejected:
        lead.stage = LeadStage.LOST
        await lead.save()
        return lead, []

    conversation = await Conversation.find_one(
        {"lead_id": lead.id},
        sort="-created_at",
    )
    if not conversation:
        await lead.save()
        return lead, []

    last_customer_message = await Message.find_one(
        {"conversation_id": conversation.id, "role": "customer"},
        sort="-created_at",
    )
    if not last_customer_message:
        await lead.save()
        return lead, []

    state = {
        "lead": {
            "id": str(lead.id),
            "business_id": str(lead.business_id),
            "source": lead.source.value if hasattr(lead.source, "value") else str(lead.source),
            "customer_name": lead.customer_name,
            "customer_phone": lead.customer_phone,
            "customer_email": lead.customer_email,
            "message": last_customer_message.content,
            "details": lead.details or {},
            "conversation_history": [{"role": "customer", "content": last_customer_message.content}],
        }
    }
    state = await OutreachAgent().run(state)

    sent = []
    dispatcher = get_communication_service()
    for item in state.get("lead", {}).get("conversation_history", []):
        if item.get("role") != "ai":
            continue
        result = await dispatcher.send_customer_message(
            {
                "source": lead.source.value if hasattr(lead.source, "value") else str(lead.source),
                "customer_phone": lead.customer_phone,
                "customer_email": lead.customer_email,
                "details": lead.details or {},
            },
            item.get("content", ""),
        )
        await append_message(
            conversation.id,
            role="ai",
            channel=result["channel"],
            content=item.get("content", ""),
        )
        sent.append(result)

    await lead.save()
    return lead, sent


async def pipeline_counts(business_id: PydanticObjectId | None = None) -> dict:
    """Get counts per pipeline stage using MongoDB aggregation."""
    match_stage: dict = {}
    if business_id:
        match_stage["business_id"] = business_id

    pipeline = []
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline.append({"$group": {"_id": "$stage", "count": {"$sum": 1}}})

    results = await Lead.aggregate(pipeline).to_list()

    counts = {"new": 0, "contacted": 0, "qualified": 0, "proposal": 0, "won": 0, "lost": 0}
    for row in results:
        stage_val = row["_id"]
        if hasattr(stage_val, "value"):
            stage_val = stage_val.value
        if stage_val in counts:
            counts[stage_val] = row["count"]
    return counts