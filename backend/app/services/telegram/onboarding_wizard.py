"""Telegram onboarding wizard — guides a business owner through setup via chat."""

from __future__ import annotations

import io
import secrets
import traceback

import qrcode  # type: ignore
import qrcode.constants  # type: ignore

from app.config import get_settings
from app.models.business import Business
from app.models.onboarding_session import (
    OnboardingSession,
    WIZARD_STEPS,
    WIZARD_QUESTIONS,
)

settings = get_settings()

# ── Industry capture-field presets ──
INDUSTRY_DEFAULTS: dict[str, dict[str, bool]] = {
    "restaurant": {
        "guest_count": True,
        "date": True,
        "time": True,
        "event_type": True,
        "dietary_restrictions": False,
        "budget": False,
    },
    "hotel": {
        "guest_count": True,
        "check_in": True,
        "check_out": True,
        "room_type": False,
        "budget": False,
    },
    "real_estate": {
        "property_type": True,
        "location": True,
        "budget": True,
        "bedrooms": False,
    },
}


# ── Deep-link helpers ──

def _generate_deep_link_code() -> str:
    return secrets.token_urlsafe(8)


def _telegram_link(code: str) -> str:
    username = settings.TELEGRAM_BOT_USERNAME
    if not username:
        return f"?start={code}"
    return f"https://t.me/{username}?start={code}"


def _owner_telegram_link(code: str) -> str:
    username = settings.TELEGRAM_BOT_USERNAME
    if not username:
        return f"?start=connect_{code}"
    return f"https://t.me/{username}?start=connect_{code}"


def _qr_code_bytes(data: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


# ── Public API ──

async def is_in_onboarding(chat_id: str) -> bool:
    """Return True if this chat_id has an active onboarding session."""
    try:
        session = await OnboardingSession.find_one({"telegram_chat_id": chat_id})
        return session is not None
    except Exception:
        return False


async def start_onboarding(chat_id: str, bot) -> None:
    """Start (or restart) the onboarding wizard for this owner."""
    # Clear any existing session for this chat
    try:
        existing = await OnboardingSession.find_one({"telegram_chat_id": chat_id})
        if existing:
            await existing.delete()
    except Exception:
        pass

    session = OnboardingSession(
        telegram_chat_id=chat_id,
        step=WIZARD_STEPS[0],
        data={},
    )
    await session.insert()

    await bot.send_message(chat_id, WIZARD_QUESTIONS[WIZARD_STEPS[0]], parse_mode="Markdown")


async def handle_onboarding_reply(chat_id: str, text: str, bot) -> None:
    """Process an owner's reply during onboarding, advance wizard, or finish."""
    session = await OnboardingSession.find_one({"telegram_chat_id": chat_id})
    if not session:
        return

    current_step = session.step
    answer = text.strip()

    # Normalise "skip" to None for optional fields
    optional_steps = {"phone", "email", "business_hours"}
    if answer.lower() == "skip" and current_step in optional_steps:
        value = None
    elif current_step == "questions":
        # Parse multi-line questions — one per line
        lines = [line.strip() for line in answer.split("\n") if line.strip()]
        if not lines:
            await bot.send_message(
                chat_id,
                "Please enter at least one question, one per line.",
            )
            return
        value = lines[:5]  # Cap at 5 questions
    else:
        value = answer

    # Store answer
    data = dict(session.data)
    data[current_step] = value
    session.data = data

    # Advance to next step
    current_index = WIZARD_STEPS.index(current_step)
    next_index = current_index + 1

    if next_index < len(WIZARD_STEPS):
        session.step = WIZARD_STEPS[next_index]
        await session.save()
        await bot.send_message(
            chat_id,
            WIZARD_QUESTIONS[WIZARD_STEPS[next_index]],
            parse_mode="Markdown",
        )
    else:
        # All questions answered — create the business
        try:
            await _finish_onboarding(chat_id, session, bot)
        except Exception as exc:
            print(f"ERROR in _finish_onboarding: {traceback.format_exc()}")
            await bot.send_message(
                chat_id,
                f"Something went wrong while setting up your business. Error: {exc}\n\nPlease try /register again.",
            )
            await session.delete()


async def _finish_onboarding(chat_id: str, session: OnboardingSession, bot) -> None:
    """Create the Business document and send the owner their QR code + links."""
    data = session.data

    # Generate a unique deep_link_code
    code = _generate_deep_link_code()
    while await Business.find_one({"deep_link_code": code}):
        code = _generate_deep_link_code()

    industry = (data.get("industry") or "other").lower().strip().replace(" ", "_")
    valid_industries = {"restaurant", "hotel", "real_estate", "other"}
    if industry not in valid_industries:
        industry = "other"

    capture_fields = INDUSTRY_DEFAULTS.get(industry, {})
    capture_questions = data.get("questions", [])

    business = Business(
        name=data.get("name", "My Business"),
        industry=industry,
        phone=data.get("phone"),
        email=data.get("email"),
        business_hours=data.get("business_hours"),
        services_offered=data.get("services"),
        welcome_message=data.get("welcome_message"),
        capture_fields=capture_fields,
        capture_questions=capture_questions,
        deep_link_code=code,
        telegram_chat_id=chat_id,   # auto-connect owner notifications
        is_active=True,
        onboarding_complete=True,
    )
    await business.insert()

    # Clean up session
    await session.delete()

    # Build links
    customer_link = _telegram_link(code)
    qr_bytes = _qr_code_bytes(customer_link)

    # Format questions list
    q_list = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(capture_questions))

    # Send confirmation (plain text to avoid Markdown parsing issues)
    summary = (
        f"🎉 {business.name} is ready!\n\n"
        f"Industry: {business.industry}\n"
        f"Services: {business.services_offered or '—'}\n"
        f"Hours: {business.business_hours or '—'}\n\n"
        f"AI Questions for customers:\n{q_list}\n\n"
        f"Customer Link (share this):\n{customer_link}\n\n"
        f"📌 The QR code below is for customers to scan and chat with your AI agent.\n\n"
        f"Commands you can use here:\n"
        f"  today — pipeline summary\n"
        f"  leads — recent leads\n"
        f"  approve <id> — approve a lead\n"
        f"  reject <id> — reject a lead\n"
        f"  won <id> <amount> — mark as won\n\n"
        f"To re-register, send /register again."
    )
    await bot.send_message(chat_id, summary)

    # Send QR code as photo
    try:
        await bot.send_photo(chat_id, qr_bytes, caption=f"Customer QR Code — {business.name}")
    except Exception as exc:
        print(f"Failed to send QR photo: {exc}")
        await bot.send_message(chat_id, f"Customer link: {customer_link}")
