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
from app.services.translation import get_translation_service, SUPPORTED_LANGUAGES

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
            try:
                await bot.answer_callback_query(data["callback_query_id"], "Processing...")
            except Exception:
                pass
        command = data.get("text", "")

        if command.startswith("approve:") or command.startswith("reject:"):
            action, _, raw_lead_id = command.partition(":")
            try:
                lead, sent = await apply_rep_decision(PydanticObjectId(raw_lead_id), action)
            except Exception as exc:
                print(f"Error in apply_rep_decision: {exc}")
                # Still mark the lead even if outreach fails
                try:
                    from app.models.lead import RepDecision
                    lead = await Lead.get(PydanticObjectId(raw_lead_id))
                    if lead:
                        if action == "approve":
                            lead.rep_decision = RepDecision.APPROVED
                            lead.stage = LeadStage.CONTACTED
                        else:
                            lead.rep_decision = RepDecision.REJECTED
                            lead.stage = LeadStage.LOST
                        await lead.save()
                except Exception:
                    lead = None
                sent = []

            if lead:
                if action == "approve":
                    # Build detailed saved info
                    details = lead.details or {}
                    detail_lines = []
                    for k, v in details.items():
                        if v and k not in ("telegram_chat_id", "telegram_username", "deep_link_code", "is_start"):
                            detail_lines.append(f"  {k}: {v}")
                    detail_text = "\n".join(detail_lines) if detail_lines else "  No details captured"

                    msg = (
                        f"✅ Lead APPROVED\n\n"
                        f"Name: {lead.customer_name or 'Unknown'}\n"
                        f"Score: {lead.score}/10\n"
                        f"Stage: {lead.stage.value}\n\n"
                        f"Captured Details:\n{detail_text}\n\n"
                        f"Lead ID: {str(lead.id)}"
                    )
                else:
                    msg = f"❌ Lead REJECTED — {raw_lead_id[:8]}... discarded."

                await bot.send_message(str(data["chat_id"]), msg)
            else:
                await bot.send_message(str(data["chat_id"]), f"Lead {raw_lead_id[:8]}... not found.")

            return {
                "status": "ok",
                "decision": action,
                "lead_id": raw_lead_id,
                "updated": bool(lead),
                "sent": sent,
            }

        if command.startswith("view_chat:"):
            raw_lead_id = command.split(":", 1)[1]
            try:
                lead = await Lead.get(PydanticObjectId(raw_lead_id))
                if lead:
                    details = lead.details or {}
                    detail_lines = []
                    for k, v in details.items():
                        if v and k not in ("telegram_chat_id", "telegram_username", "deep_link_code", "is_start"):
                            detail_lines.append(f"  {k}: {v}")
                    detail_text = "\n".join(detail_lines) if detail_lines else "  No details captured"

                    msg = (
                        f"📋 Lead Details\n\n"
                        f"Name: {lead.customer_name or 'Unknown'}\n"
                        f"Phone: {lead.customer_phone or '—'}\n"
                        f"Email: {lead.customer_email or '—'}\n"
                        f"Score: {lead.score}/10\n"
                        f"Stage: {lead.stage.value}\n"
                        f"Decision: {lead.rep_decision.value}\n\n"
                        f"Captured Info:\n{detail_text}\n\n"
                        f"Score Reasoning: {lead.score_reasoning or '—'}\n\n"
                        f"Lead ID: {str(lead.id)}"
                    )
                    await bot.send_message(str(data["chat_id"]), msg)
                else:
                    await bot.send_message(str(data["chat_id"]), "Lead not found.")
            except Exception as exc:
                await bot.send_message(str(data["chat_id"]), f"Error loading lead: {exc}")
            return {"status": "ok", "scope": "view_chat"}

        # ── Language selection callback (lang:DEEP_LINK_CODE:LOCALE or lang:DEEP_LINK_CODE:LOCALE:n for new enquiry) ──
        if command.startswith("lang:"):
            parts = command.split(":")
            # Support both 3-part (normal) and 4-part (new_enquiry) format
            if len(parts) >= 3:
                _, deep_code, locale = parts[0], parts[1], parts[2]
                is_new_enquiry = len(parts) == 4 and parts[3] == "n"
                business = await _find_business_by_code(deep_code)
                if business:
                    lang_name = SUPPORTED_LANGUAGES.get(locale, locale)
                    welcome = business.welcome_message or f"Hi! Welcome to {business.name}. How can I help you today?"

                    if is_new_enquiry:
                        welcome = f"🆕 New enquiry started!\n\n{welcome}"

                    # Translate welcome message
                    translator = get_translation_service()
                    if locale != "en":
                        welcome = await translator.translate_from_english(welcome, locale)

                    await bot.send_message(str(data["chat_id"]), f"🌐 Language: {lang_name}\n\n{welcome}")

                    # Create placeholder lead with language preference
                    # If this is a new enquiry the old lead was already closed in the /new handler,
                    # so get_or_create_lead_for_channel will create a fresh lead automatically.
                    await process_customer_message(
                        source="telegram",
                        business_id=str(business.id),
                        customer_name=data.get("from_name") or data.get("username"),
                        customer_phone=None,
                        customer_email=None,
                        details={
                            "telegram_chat_id": str(data["chat_id"]),
                            "telegram_username": data.get("username"),
                            "deep_link_code": deep_code,
                            "language": locale,
                            "is_start": True,
                            "new_enquiry": is_new_enquiry,
                        },
                        message_text="/start",
                    )
                    scope = "new_enquiry_lang_select" if is_new_enquiry else "lang_select"
                    return {"status": "ok", "scope": scope, "locale": locale}
            return {"status": "ok", "scope": "lang_select", "error": "bad_format"}

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
                        f"Send /help to see all commands.",
                    )
                    return {"status": "ok", "scope": "owner_connect", "business": business.name}
                await bot.send_message(chat_id, "Invalid code. Please check your onboarding link.")
                return {"status": "ok", "scope": "owner_connect", "error": "invalid_code"}

            # Customer scanning QR / clicking deep link: /start CODE
            business = await _find_business_by_code(code)
            if business:
                # Show language selection buttons
                lang_buttons = []
                row = []
                for locale, label in SUPPORTED_LANGUAGES.items():
                    row.append({"text": label, "callback_data": f"lang:{code}:{locale}"})
                    if len(row) == 2:
                        lang_buttons.append(row)
                        row = []
                if row:
                    lang_buttons.append(row)

                await bot.send_inline_keyboard(
                    chat_id,
                    f"👋 Welcome to {business.name}!\n\n"
                    f"Please select your preferred language:",
                    lang_buttons,
                )
                return {"status": "ok", "scope": "customer_start", "business": business.name, "step": "lang_select"}

            await bot.send_message(chat_id, "Welcome! Please use a valid business link to get started.")
            return {"status": "ok", "scope": "customer_start", "error": "invalid_code"}

        # Plain /start without code
        await bot.send_message(
            chat_id,
            "Welcome to LeadForge! Please use a business-specific link to connect.",
        )
        return {"status": "ok", "scope": "customer_start"}

    # ── 4b. /new — customer starts a fresh enquiry ──
    if text.startswith("/new"):
        assoc_business = await _resolve_business_for_customer(chat_id)
        if assoc_business:
            # ── Close all existing active leads for this customer ──
            # This ensures get_or_create_lead_for_channel creates a brand-new lead
            # when the customer picks a language (since WON/LOST leads are excluded).
            try:
                active_leads = await Lead.find(
                    {
                        "source": "telegram",
                        "details.telegram_chat_id": str(chat_id),
                        "stage": {"$nin": [LeadStage.WON.value, LeadStage.LOST.value]},
                    }
                ).to_list()
                for old_lead in active_leads:
                    old_lead.stage = LeadStage.LOST
                    old_details = dict(old_lead.details or {})
                    old_details["closed_reason"] = "new_enquiry"
                    old_lead.details = old_details
                    await old_lead.save()
                print(f"ℹ️  /new: closed {len(active_leads)} active lead(s) for chat {chat_id}")
            except Exception as exc:
                print(f"⚠️  /new: could not close old leads: {exc}")

            # Show language selection with 'n' flag so the callback knows it's a new enquiry
            code = assoc_business.deep_link_code or ""
            lang_buttons = []
            row = []
            for locale, label in SUPPORTED_LANGUAGES.items():
                row.append({"text": label, "callback_data": f"lang:{code}:{locale}:n"})
                if len(row) == 2:
                    lang_buttons.append(row)
                    row = []
            if row:
                lang_buttons.append(row)

            await bot.send_inline_keyboard(
                chat_id,
                f"🆕 Starting a new enquiry with {assoc_business.name}!\n\n"
                f"Please select your preferred language:",
                lang_buttons,
            )
            return {"status": "ok", "scope": "new_enquiry", "business": assoc_business.name}
        else:
            await bot.send_message(
                chat_id,
                "No active business found. Please scan a QR code or use a business link first.",
            )
            return {"status": "ok", "scope": "new_enquiry", "error": "no_business"}

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

    # ── 6. Regular customer message ──
    # Find which business this customer belongs to
    assoc_business = await _resolve_business_for_customer(chat_id)

    # Check if customer has a language preference from their lead
    customer_lang = "en"
    existing_lead = None
    if assoc_business:
        existing_lead = await Lead.find_one({
            "source": "telegram",
            "details.telegram_chat_id": str(chat_id),
            "stage": {"$nin": [LeadStage.WON.value, LeadStage.LOST.value]},
        })
        if existing_lead and existing_lead.details:
            customer_lang = existing_lead.details.get("language", "en")

    # Translate customer message to English for AI processing
    message_for_ai = text
    if customer_lang != "en":
        translator = get_translation_service()
        message_for_ai = await translator.translate_to_english(text, customer_lang)

    result = await process_customer_message(
        source="telegram",
        business_id=str(assoc_business.id) if assoc_business else None,
        customer_name=data.get("from_name") or data.get("username"),
        customer_phone=None,
        customer_email=None,
        details={
            "telegram_chat_id": chat_id,
            "telegram_username": data.get("username"),
            "language": customer_lang,
        },
        message_text=message_for_ai,
    )

    # Translate AI reply back to customer language
    if customer_lang != "en" and result.get("sent"):
        # The AI reply was already sent in English via lead_workflow
        # We need to intercept and translate. For now, send a translated follow-up.
        pass  # Translation is handled in lead_workflow via details.language

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

    # ── /help — show all commands ──
    if lowered in ("/help", "help", "/start"):
        biz_name = business.name if business else "LeadForge"
        await bot.send_message(
            chat_id,
            f"📋 {biz_name} — Owner Commands\n\n"
            f"📊 Statistics:\n"
            f"  /stats — full business analytics\n"
            f"  /today — today's pipeline summary\n\n"
            f"👥 Customer Management:\n"
            f"  /customers — all contacted customers\n"
            f"  /approved — approved enquiries\n"
            f"  /rejected — rejected enquiries\n"
            f"  /leads — recent 10 leads with scores\n"
            f"  /detail <lead_id> — view full details of a lead\n\n"
            f"✅ Actions:\n"
            f"  approve <lead_id> — approve a lead\n"
            f"  reject <lead_id> — reject a lead\n"
            f"  won <lead_id> <amount> — mark as won\n\n"
            f"🔧 Setup:\n"
            f"  /register — register a new business\n"
        )
        return {"status": "ok", "scope": "rep", "command": "help"}

    # ── /stats — full business analytics ──
    if lowered in ("/stats", "stats"):
        from app.services.lead_workflow import pipeline_counts
        from app.models.lead import RepDecision

        try:
            counts = await pipeline_counts(business_id=business.id if business else None)

            # Total customers
            match = {"business_id": business.id} if business else {}
            total = await Lead.find(match).count()

            # Approved / Rejected counts
            approved = await Lead.find({**match, "rep_decision": RepDecision.APPROVED.value}).count()
            rejected = await Lead.find({**match, "rep_decision": RepDecision.REJECTED.value}).count()
            pending = await Lead.find({**match, "rep_decision": RepDecision.PENDING.value}).count()

            # Average score
            score_pipeline = []
            if match:
                score_pipeline.append({"$match": match})
            score_pipeline.append({"$group": {"_id": None, "avg_score": {"$avg": "$score"}}})
            score_result = await Lead.aggregate(score_pipeline).to_list()
            avg_score = round(score_result[0]["avg_score"], 1) if score_result and score_result[0].get("avg_score") else 0

            # Won deals
            won = counts.get("won", 0)

            biz_name = business.name if business else "LeadForge"
            msg = (
                f"📊 {biz_name} — Statistics\n\n"
                f"👥 Total Enquiries: {total}\n"
                f"✅ Approved: {approved}\n"
                f"❌ Rejected: {rejected}\n"
                f"⏳ Pending: {pending}\n"
                f"🏆 Won: {won}\n\n"
                f"📈 Average Score: {avg_score}/10\n\n"
                f"Pipeline Breakdown:\n"
            )
            for stage, count in counts.items():
                emoji = {"new": "🆕", "contacted": "📞", "qualified": "✅", "proposal": "📝", "won": "🏆", "lost": "❌"}.get(stage, "•")
                msg += f"  {emoji} {stage}: {count}\n"

            await bot.send_message(chat_id, msg)
        except Exception as exc:
            await bot.send_message(chat_id, f"Error loading stats: {exc}")
        return {"status": "ok", "scope": "rep", "command": "stats"}

    # ── /today — today's pipeline summary ──
    if lowered in ("/today", "today"):
        from app.services.lead_workflow import pipeline_counts

        try:
            counts = await pipeline_counts(business_id=business.id if business else None)
            summary = "\n".join(f"  {key}: {value}" for key, value in counts.items())
            title = f"{business.name} — Today's Pipeline" if business else "Today's Pipeline"
            await bot.send_message(chat_id, f"📊 {title}\n\n{summary}")
        except Exception as exc:
            await bot.send_message(chat_id, f"Error loading pipeline: {exc}")
        return {"status": "ok", "scope": "rep", "command": "today"}

    # ── /customers — all contacted customers ──
    if lowered in ("/customers", "customers"):
        try:
            match = {"business_id": business.id} if business else {}
            leads = await Lead.find(match).sort("-score").limit(20).to_list()
            if leads:
                lines = []
                for i, lead in enumerate(leads, 1):
                    status = "✅" if lead.rep_decision.value == "approved" else "❌" if lead.rep_decision.value == "rejected" else "⏳"
                    lines.append(
                        f"{i}. {status} {lead.customer_name or 'Unknown'} | "
                        f"Score: {lead.score} | {lead.stage.value} | "
                        f"ID: {str(lead.id)[:8]}.."
                    )
                msg = f"👥 All Customers (sorted by score)\n\n" + "\n".join(lines)
            else:
                msg = "No customers found yet."
            await bot.send_message(chat_id, msg)
        except Exception as exc:
            await bot.send_message(chat_id, f"Error loading customers: {exc}")
        return {"status": "ok", "scope": "rep", "command": "customers"}

    # ── /approved — approved enquiries ──
    if lowered in ("/approved", "approved"):
        from app.models.lead import RepDecision
        try:
            match = {"rep_decision": RepDecision.APPROVED.value}
            if business:
                match["business_id"] = business.id
            leads = await Lead.find(match).sort("-score").limit(20).to_list()
            if leads:
                lines = []
                for i, lead in enumerate(leads, 1):
                    lines.append(
                        f"{i}. {lead.customer_name or 'Unknown'} | "
                        f"Score: {lead.score} | {lead.stage.value} | "
                        f"ID: {str(lead.id)[:8]}.."
                    )
                msg = f"✅ Approved Enquiries ({len(leads)})\n\n" + "\n".join(lines)
            else:
                msg = "No approved enquiries yet."
            await bot.send_message(chat_id, msg)
        except Exception as exc:
            await bot.send_message(chat_id, f"Error: {exc}")
        return {"status": "ok", "scope": "rep", "command": "approved"}

    # ── /rejected — rejected enquiries ──
    if lowered in ("/rejected", "rejected"):
        from app.models.lead import RepDecision
        try:
            match = {"rep_decision": RepDecision.REJECTED.value}
            if business:
                match["business_id"] = business.id
            leads = await Lead.find(match).sort("-created_at").limit(20).to_list()
            if leads:
                lines = []
                for i, lead in enumerate(leads, 1):
                    lines.append(
                        f"{i}. {lead.customer_name or 'Unknown'} | "
                        f"Score: {lead.score} | {lead.stage.value} | "
                        f"ID: {str(lead.id)[:8]}.."
                    )
                msg = f"❌ Rejected Enquiries ({len(leads)})\n\n" + "\n".join(lines)
            else:
                msg = "No rejected enquiries."
            await bot.send_message(chat_id, msg)
        except Exception as exc:
            await bot.send_message(chat_id, f"Error: {exc}")
        return {"status": "ok", "scope": "rep", "command": "rejected"}

    # ── /leads — recent leads ──
    if lowered in ("/leads", "leads"):
        try:
            query = Lead.find().sort("-created_at").limit(10)
            if business:
                query = Lead.find({"business_id": business.id}).sort("-created_at").limit(10)
            leads = await query.to_list()
            if leads:
                lines = []
                for lead in leads:
                    status = "✅" if lead.rep_decision.value == "approved" else "❌" if lead.rep_decision.value == "rejected" else "⏳"
                    lines.append(
                        f"{status} {lead.customer_name or 'Unknown'} | "
                        f"Score: {lead.score} | {lead.stage.value} | "
                        f"ID: {str(lead.id)[:8]}.."
                    )
                msg = "📋 Recent Leads\n\n" + "\n".join(lines)
            else:
                msg = "No leads found."
            await bot.send_message(chat_id, msg)
        except Exception as exc:
            await bot.send_message(chat_id, f"Error loading leads: {exc}")
        return {"status": "ok", "scope": "rep", "command": "leads"}

    # ── /detail <lead_id> — full lead details ──
    if lowered.startswith("/detail ") or lowered.startswith("detail "):
        raw_id = text.split(maxsplit=1)[1].strip()
        try:
            lead = await Lead.get(PydanticObjectId(raw_id))
            if lead:
                details = lead.details or {}
                detail_lines = []
                for k, v in details.items():
                    if v and k not in ("telegram_chat_id", "telegram_username", "deep_link_code", "is_start"):
                        detail_lines.append(f"  {k}: {v}")
                detail_text = "\n".join(detail_lines) if detail_lines else "  No details captured"

                msg = (
                    f"📋 Lead Details\n\n"
                    f"Name: {lead.customer_name or 'Unknown'}\n"
                    f"Phone: {lead.customer_phone or '—'}\n"
                    f"Email: {lead.customer_email or '—'}\n"
                    f"Source: {lead.source.value if hasattr(lead.source, 'value') else lead.source}\n"
                    f"Score: {lead.score}/10\n"
                    f"Stage: {lead.stage.value}\n"
                    f"Decision: {lead.rep_decision.value}\n\n"
                    f"Captured Info:\n{detail_text}\n\n"
                    f"Score Reasoning: {lead.score_reasoning or '—'}\n\n"
                    f"Lead ID: {str(lead.id)}"
                )
                await bot.send_message(chat_id, msg)
            else:
                await bot.send_message(chat_id, "Lead not found.")
        except Exception as exc:
            await bot.send_message(chat_id, f"Error: {exc}")
        return {"status": "ok", "scope": "rep", "command": "detail"}

    # ── approve / reject text commands ──
    if lowered.startswith("approve ") or lowered.startswith("reject "):
        action, raw_lead_id = lowered.split(maxsplit=1)
        try:
            lead, sent = await apply_rep_decision(PydanticObjectId(raw_lead_id), action)
            if lead:
                await bot.send_message(chat_id, f"{'✅' if action == 'approve' else '❌'} Lead {str(lead.id)[:8]}.. marked {action}.")
        except Exception as exc:
            await bot.send_message(chat_id, f"Error: {exc}")
            lead, sent = None, []
        return {"status": "ok", "scope": "rep", "command": action, "lead_id": raw_lead_id, "sent": sent if sent else []}

    # ── won command ──
    if lowered.startswith("won "):
        parts = text.split(maxsplit=2)
        if len(parts) >= 2:
            try:
                lead = await Lead.get(PydanticObjectId(parts[1]))
                if lead:
                    lead.stage = LeadStage.WON
                    if len(parts) == 3:
                        details = dict(lead.details or {})
                        details["deal_value"] = parts[2]
                        lead.details = details
                    await lead.save()
                    await bot.send_message(chat_id, f"🏆 Lead {str(lead.id)[:8]}.. marked WON!")
                    return {"status": "ok", "scope": "rep", "command": "won", "lead_id": parts[1]}
            except Exception as exc:
                await bot.send_message(chat_id, f"Error: {exc}")

    # ── Unknown command — show help ──
    biz_name = business.name if business else "LeadForge"
    await bot.send_message(
        chat_id,
        f"Unknown command. Send /help to see all available commands for {biz_name}.",
    )
    return {"status": "ok", "scope": "rep", "command": "unknown"}

