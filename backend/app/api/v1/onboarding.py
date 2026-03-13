"""Onboarding endpoints for business registration and configuration."""

from __future__ import annotations

import base64
import io
import secrets

import qrcode  # type: ignore
import qrcode.constants  # type: ignore
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import get_settings
from app.models.business import Business

router = APIRouter()
settings = get_settings()

# ── Default capture-field presets by industry ──
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


# ── Schemas ──


class RegisterPayload(BaseModel):
    name: str
    industry: str = "other"
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    business_hours: str | None = None
    services_offered: str | None = None


class ConfigurePayload(BaseModel):
    business_id: str
    capture_fields: dict[str, bool]
    welcome_message: str | None = None


# ── Helpers ──


def _generate_deep_link_code() -> str:
    """Generate a short, URL-safe unique code."""
    return secrets.token_urlsafe(8)  # ~11 chars


def _telegram_link(code: str) -> str:
    username = settings.TELEGRAM_BOT_USERNAME
    if not username:
        return f"(set TELEGRAM_BOT_USERNAME in .env) ?start={code}"
    return f"https://t.me/{username}?start={code}"


def _owner_telegram_link(code: str) -> str:
    """Owner-specific deep link that auto-routes to notification connect flow."""
    username = settings.TELEGRAM_BOT_USERNAME
    if not username:
        return f"(set TELEGRAM_BOT_USERNAME in .env) ?start=connect_{code}"
    return f"https://t.me/{username}?start=connect_{code}"


def _qr_code_bytes(data: str) -> bytes:
    """Generate a QR code PNG in memory."""
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


# ── Endpoints ──


@router.post("/register")
async def register_business(payload: RegisterPayload):
    """Register a new business and return Telegram deep link + QR code."""
    code = _generate_deep_link_code()

    # Ensure uniqueness (extremely unlikely collision)
    while await Business.find_one({"deep_link_code": code}):
        code = _generate_deep_link_code()

    industry = payload.industry.lower().strip()
    default_fields = INDUSTRY_DEFAULTS.get(industry, {})

    business = Business(
        name=payload.name,
        industry=industry,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        business_hours=payload.business_hours,
        services_offered=payload.services_offered,
        capture_fields=default_fields,
        deep_link_code=code,
        is_active=True,
        onboarding_complete=False,
    )
    await business.insert()

    customer_link = _telegram_link(code)
    owner_link = _owner_telegram_link(code)
    qr_b64 = base64.b64encode(_qr_code_bytes(customer_link)).decode()

    return {
        "business_id": str(business.id),
        "deep_link_code": code,
        "telegram_link": customer_link,
        "owner_telegram_link": owner_link,
        "qr_code_base64": qr_b64,
        "default_capture_fields": default_fields,
        "next_step": (
            "1. Owner: open owner_telegram_link and press Start (auto-connect). "
            "2. Customers: share telegram_link / QR so they can chat with your AI assistant."
        ),
    }


@router.post("/configure")
async def configure_business(payload: ConfigurePayload):
    """Set capture fields and optional welcome message for a business."""
    business = await Business.get(PydanticObjectId(payload.business_id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    business.capture_fields = payload.capture_fields
    if payload.welcome_message:
        business.welcome_message = payload.welcome_message
    business.onboarding_complete = True
    await business.save()
    return {
        "business_id": str(business.id),
        "capture_fields": business.capture_fields,
        "onboarding_complete": True,
    }


@router.get("/{business_id}/qr-code")
async def get_qr_code(business_id: str):
    """Return QR code image as PNG for the business's Telegram deep link."""
    business = await Business.get(PydanticObjectId(business_id))
    if not business or not business.deep_link_code:
        raise HTTPException(status_code=404, detail="Business not found")

    link = _telegram_link(business.deep_link_code)
    png_bytes = _qr_code_bytes(link)
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")


@router.get("/{business_id}/status")
async def onboarding_status(business_id: str):
    """Return current onboarding status for a business."""
    business = await Business.get(PydanticObjectId(business_id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    link = _telegram_link(business.deep_link_code) if business.deep_link_code else None
    owner_link = _owner_telegram_link(business.deep_link_code) if business.deep_link_code else None
    return {
        "business_id": str(business.id),
        "name": business.name,
        "industry": business.industry,
        "telegram_link": link,
        "owner_telegram_link": owner_link,
        "telegram_connected": bool(business.telegram_chat_id),
        "capture_fields": business.capture_fields or {},
        "onboarding_complete": business.onboarding_complete,
    }
