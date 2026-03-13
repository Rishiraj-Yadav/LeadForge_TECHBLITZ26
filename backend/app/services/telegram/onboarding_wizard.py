"""Telegram onboarding wizard — guides a business owner through setup via chat."""

from __future__ import annotations

import io
import secrets

import qrcode  # type: ignore
import qrcode.constants  # type: ignore

from app.config import get_settings
from app.models.business import Business
from app.models.onboarding_session import (
    OnboardingSession,
    WIZARD_STEPS,
    WIZARD_QUESTIONS,
)
from app.api.v1.onboarding import INDUSTRY_DEFAULTS

settings = get_settings()


# ── Deep-link helpers (same logic as onboarding.py REST helpers) ──

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
    session = await OnboardingSession.find_one({"telegram_chat_id": chat_id})
    return session is not None


async def start_onboarding(chat_id: str, bot) -> None:
    """Start (or restart) the onboarding wizard for this owner."""
    # Clear any existing session for this chat
    existing = await OnboardingSession.find_one({"telegram_chat_id": chat_id})
    if existing:
        await existing.delete()

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
    value = None if (answer.lower() == "skip" and current_step in optional_steps) else answer

    # Store answer
    session.data[current_step] = value

    # Advance to next step
    current_index = WIZARD_STEPS.index(current_step)
    next_index = current_index + 1

    if next_index < len(WIZARD_STEPS):
        # More questions to ask
        session.step = WIZARD_STEPS[next_index]
        await session.save()
        await bot.send_message(
            chat_id,
            WIZARD_QUESTIONS[WIZARD_STEPS[next_index]],
            parse_mode="Markdown",
        )
    else:
        # All questions answered — create the business
        await _finish_onboarding(chat_id, session, bot)


async def _finish_onboarding(chat_id: str, session: OnboardingSession, bot) -> None:
    """Create the Business document and send the owner their QR code + links."""
    data = session.data

    # Generate a unique deep_link_code
    code = _generate_deep_link_code()
    while await Business.find_one({"deep_link_code": code}):
        code = _generate_deep_link_code()

    industry = (data.get("industry") or "other").lower().strip()
    valid_industries = {"restaurant", "hotel", "real_estate", "other"}
    if industry not in valid_industries:
        industry = "other"

    capture_fields = INDUSTRY_DEFAULTS.get(industry, {})

    business = Business(
        name=data.get("name", "My Business"),
        industry=industry,
        phone=data.get("phone"),
        email=data.get("email"),
        business_hours=data.get("business_hours"),
        services_offered=data.get("services"),
        welcome_message=data.get("welcome_message"),
        capture_fields=capture_fields,
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
    owner_link = _owner_telegram_link(code)
    qr_bytes = _qr_code_bytes(customer_link)

    # ── Send confirmation message ──
    summary = (
        f"🎉 *{business.name}* is ready!\n\n"
        f"*Industry:* {business.industry}\n"
        f"*Services:* {business.services_offered or '—'}\n"
        f"*Hours:* {business.business_hours or '—'}\n\n"
        f"*Customer Link (share this):*\n`{customer_link}`\n\n"
        f"*Owner Notifications Link:*\n`{owner_link}`\n\n"
        f"📌 The QR code below is for customers to scan and start chatting with your AI agent.\n\n"
        f"*Commands you can use here:*\n"
        f"`today` — pipeline summary\n"
        f"`leads` — recent leads\n"
        f"`approve <id>` — approve a lead\n"
        f"`reject <id>` — reject a lead\n"
        f"`won <id> <amount>` — mark as won\n\n"
        f"To re-register or change your business, send `/register` again."
    )
    await bot.send_message(chat_id, summary, parse_mode="Markdown")

    # Send QR code as photo
    await bot.send_photo(chat_id, qr_bytes, caption=f"📷 Customer QR Code — {business.name}")
