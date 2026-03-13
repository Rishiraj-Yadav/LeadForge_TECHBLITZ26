"""Webhook endpoints for Telegram, Instagram, forms, and email."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from beanie import PydanticObjectId

from app.config import get_settings
from app.models.business import Business
from app.models.lead import Lead, LeadStage
from app.schemas.webhook import FormSubmission
from app.services.instagram.client import get_instagram_client
from app.services.lead_workflow import process_customer_message, apply_rep_decision
from app.services.telegram.bot import get_telegram_bot
from app.services.telegram.onboarding_wizard import (
    is_in_onboarding,
    start_onboarding,
    handle_onboarding_reply,
)

router = APIRouter()
settings = get_settings()


# ── Helper: look up business from deep_link_code ──


async def _find_business_by_code(code: str) -> Business | None:
    return await Business.find_one({"deep_link_code": code})


async def _find_business_by_rep_chat(chat_id: str) -> Business | None:
    """Check if a chat_id belongs to any business owner."""
    return await Business.find_one({"telegram_chat_id": str(chat_id)})


async def _resolve_business_for_customer(chat_id: str) -> Business | None:
    """Find the business a customer is associated with via their existing lead."""
    # Use raw MongoDB query — Beanie has no .not_in() on ExpressionField
    lead = await Lead.find_one(
        {
            "source": "telegram",
            "details.telegram_chat_id": str(chat_id),
            "stage": {"$nin": [LeadStage.WON.value, LeadStage.LOST.value]},
        }
    )
    if lead:
        return await Business.get(lead.business_id)
    return None


# ── Telegram Webhook ──


@router.post("/telegram")
async def telegram_webhook(
    payload: dict,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if (
        settings.TELEGRAM_WEBHOOK_SECRET
        and x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET
    ):
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    bot = get_telegram_bot()
    data = bot.parse_webhook(payload)

    # Extract early so we can use for error messages
    text = (data.get("text") or "").strip()
    chat_id = str(data.get("chat_id", ""))

    try:
        return await _handle_telegram_update(bot, data, text, chat_id)
    except Exception as exc:
        # Gracefully handle DB-not-connected or any other error
        print(f"⚠️  Telegram webhook error: {exc}")
        try:
            if chat_id:
                await bot.send_message(
                    chat_id,
                    "⚠️ Sorry, the service is temporarily unavailable. "
                    "Please try again in a moment.",
                )
        except Exception:
            pass
        return {"status": "error", "detail": str(exc)}


async def _handle_telegram_update(bot, data: dict, text: str, chat_id: str):
    """Core Telegram update handler — separated so we can wrap with try/except."""

    # ── 1. Callback queries (approve/reject buttons) ──
    if data["type"] == "callback":
        if data.get("callback_query_id"):
            await bot.answer_callback_query(data["callback_query_id"], "Decision received")
        command = data.get("text", "")
        if command.startswith("approve:") or command.startswith("reject:"):
            action, _, raw_lead_id = command.partition(":")
            lead, sent = await apply_rep_decision(PydanticObjectId(raw_lead_id), action)
            status_msg = f"Lead {raw_lead_id[:8]}... marked {action}."
            if lead:
                await bot.send_message(str(data["chat_id"]), status_msg)
            return {
                "status": "ok",
                "decision": action,
                "lead_id": raw_lead_id,
                "updated": bool(lead),
                "sent": sent,
            }
        return {"status": "ok", "decision": command}

    # ── 2. /register — owner starts Telegram onboarding wizard ──
    if text.startswith("/register"):
        await start_onboarding(chat_id, bot)
        return {"status": "ok", "scope": "owner_onboarding", "step": "started"}

    # ── 3. Owner is mid-onboarding wizard — process their reply ──
    if await is_in_onboarding(chat_id):
        await handle_onboarding_reply(chat_id, text, bot)
        return {"status": "ok", "scope": "owner_onboarding"}

    # ── 4. /start deep link — customer or owner connecting ──
    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            code = parts[1].strip()

            # Owner connecting for notifications: /start connect_CODE
            if code.startswith("connect_"):
                real_code = code[len("connect_"):]
                business = await _find_business_by_code(real_code)
                if business:
                    business.telegram_chat_id = chat_id
                    await business.save()
                    await bot.send_message(
                        chat_id,
                        f"Connected! You will now receive lead notifications for {business.name}.\n\n"
                        f"Commands:\n"
                        f"today — pipeline summary\n"
                        f"leads — recent leads\n"
                        f"approve <id> — approve a lead\n"
                        f"reject <id> — reject a lead\n"
                        f"won <id> <amount> — mark as won",
                    )
                    return {"status": "ok", "scope": "owner_connect", "business": business.name}
                await bot.send_message(chat_id, "Invalid code. Please check your onboarding link.")
                return {"status": "ok", "scope": "owner_connect", "error": "invalid_code"}

            # Customer scanning QR / clicking deep link: /start CODE
            business = await _find_business_by_code(code)
            if business:
                welcome = business.welcome_message or (
                    f"Hi! Welcome to {business.name} "
                    f"How can I help you today?"
                )
                await bot.send_message(chat_id, welcome)
                # Create a placeholder lead so we can route future messages
                await process_customer_message(
                    source="telegram",
                    business_id=str(business.id),
                    customer_name=data.get("from_name") or data.get("username"),
                    customer_phone=None,
                    customer_email=None,
                    details={
                        "telegram_chat_id": chat_id,
                        "telegram_username": data.get("username"),
                        "deep_link_code": code,
                        "is_start": True,
                    },
                    message_text="/start",
                )
                return {"status": "ok", "scope": "customer_start", "business": business.name}

            await bot.send_message(chat_id, "Welcome! Please use a valid business link to get started.")
            return {"status": "ok", "scope": "customer_start", "error": "invalid_code"}

        # Plain /start without code
        await bot.send_message(
            chat_id,
            "Welcome to LeadForge! Please use a business-specific link to connect.",
        )
        return {"status": "ok", "scope": "customer_start"}

    # ── 3. /connect command (alternative way for owners) ──
    if text.startswith("/connect"):
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            code = parts[1].strip()
            business = await _find_business_by_code(code)
            if business:
                business.telegram_chat_id = chat_id
                await business.save()
                await bot.send_message(
                    chat_id,
                    f"Connected! You will receive notifications for {business.name}.",
                )
                return {"status": "ok", "scope": "owner_connect", "business": business.name}
        await bot.send_message(chat_id, "Usage: /connect <your_business_code>")
        return {"status": "ok", "scope": "owner_connect"}

    # ── 4. Check if this is a business owner (rep commands) ──
    business = await _find_business_by_rep_chat(chat_id)
    if not business and chat_id == settings.REP_TELEGRAM_CHAT_ID:
        # Fall back to global rep
        business = True  # sentinel
    if business:
        return await _handle_rep_command(bot, data, business if isinstance(business, Business) else None)

    # ── 5. Regular customer message ──
    # Find which business this customer belongs to
    assoc_business = await _resolve_business_for_customer(chat_id)
    result = await process_customer_message(
        source="telegram",
        business_id=str(assoc_business.id) if assoc_business else None,
        customer_name=data.get("from_name") or data.get("username"),
        customer_phone=None,
        customer_email=None,
        details={
            "telegram_chat_id": chat_id,
            "telegram_username": data.get("username"),
        },
        message_text=text,
    )
    return {
        "status": "ok",
        "scope": "customer",
        "lead_id": str(result["lead"].id),
        "sent": result["sent"],
        "stage": str(result["lead"].stage.value),
        "decision": str(result["lead"].rep_decision.value),
    }


# ── Instagram ──


@router.post("/instagram")
async def instagram_webhook(payload: dict):
    client = get_instagram_client()
    processed = []
    for message in client.parse_webhook(payload):
        result = await process_customer_message(
            source="instagram",
            business_id=None,
            customer_name=message["sender_id"],
            customer_phone=None,
            customer_email=None,
            details={"instagram_sender_id": message["sender_id"]},
            message_text=message["text"],
        )
        processed.append({"lead_id": str(result["lead"].id), "sent": result["sent"]})
    return {"status": "ok", "processed": len(processed)}


# ── Form ──


@router.post("/form")
async def form_webhook(payload: FormSubmission):
    result = await process_customer_message(
        source="form",
        business_id=payload.business_id,
        customer_name=payload.name,
        customer_phone=payload.phone,
        customer_email=payload.email,
        details={"source_url": payload.source_url},
        message_text=payload.message,
    )
    return {"status": "ok", "lead_id": str(result["lead"].id), "sent": result["sent"]}


# ── Email ──


@router.post("/email")
async def email_webhook(payload: dict):
    result = await process_customer_message(
        source="email",
        business_id=None,
        customer_name=payload.get("from_name"),
        customer_phone=None,
        customer_email=payload.get("from_email"),
        details={"subject": payload.get("subject")},
        message_text=payload.get("body", ""),
    )
    return {"status": "ok", "lead_id": str(result["lead"].id), "sent": result["sent"]}


# ── Rep command handler ──


async def _handle_rep_command(bot, data: dict, business: Business | None = None):
    """Handle commands from a business owner / rep."""
    text = (data.get("text") or "").strip()
    lowered = text.lower()
    chat_id = str(data["chat_id"])

    if lowered == "today":
        from app.services.lead_workflow import pipeline_counts

        counts = await pipeline_counts(business_id=business.id if business else None)
        summary = "\n".join(f"{key}: {value}" for key, value in counts.items())
        title = f"{business.name} Pipeline" if business else "Pipeline"
        await bot.send_message(chat_id, f"{title}\n\n{summary}")
        return {"status": "ok", "scope": "rep", "command": "today"}

    if lowered == "leads":
        query = Lead.find().sort("-created_at").limit(10)
        if business:
            query = Lead.find({"business_id": business.id}).sort("-created_at").limit(10)
        leads = await query.to_list()
        summary = "\n".join(
            f"{str(lead.id)[:8]}.. | {lead.customer_name or 'Unknown'} | {lead.stage.value} | {lead.score}"
            for lead in leads
        ) or "No leads found"
        await bot.send_message(chat_id, f"Recent leads\n\n{summary}")
        return {"status": "ok", "scope": "rep", "command": "leads"}

    if lowered.startswith("approve ") or lowered.startswith("reject "):
        action, raw_lead_id = lowered.split(maxsplit=1)
        lead, sent = await apply_rep_decision(PydanticObjectId(raw_lead_id), action)
        if lead:
            await bot.send_message(chat_id, f"Lead {str(lead.id)[:8]}.. marked {action}.")
            return {
                "status": "ok",
                "scope": "rep",
                "command": action,
                "lead_id": raw_lead_id,
                "sent": sent,
            }

    if lowered.startswith("won "):
        parts = text.split(maxsplit=2)
        if len(parts) >= 2:
            lead = await Lead.get(PydanticObjectId(parts[1]))
            if lead:
                lead.stage = LeadStage.WON
                if len(parts) == 3:
                    details = dict(lead.details or {})
                    details["deal_value"] = parts[2]
                    lead.details = details
                await lead.save()
                await bot.send_message(chat_id, f"Lead {str(lead.id)[:8]}.. marked won.")
                return {"status": "ok", "scope": "rep", "command": "won", "lead_id": parts[1]}

    await bot.send_message(
        chat_id,
        "Commands:\n"
        "today — pipeline summary\n"
        "leads — recent leads\n"
        "approve <lead_id> — approve a lead\n"
        "reject <lead_id> — reject a lead\n"
        "won <lead_id> <amount> — mark as won",
    )
    return {"status": "ok", "scope": "rep", "command": "help"}
