"""Webhook endpoints for WhatsApp, Instagram, Telegram, forms, and email."""

from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, Query

from app.agents.orchestrator import run_lead_workflow
from app.schemas.webhook import FormSubmission
from app.services.whatsapp.webhook import verify_webhook, parse_webhook_payload
from app.services.instagram.client import get_instagram_client
from app.services.telegram.bot import get_telegram_bot

router = APIRouter()


@router.get("/whatsapp")
async def verify_whatsapp(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    challenge = verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if not challenge:
        raise HTTPException(status_code=403, detail="Invalid verify token")
    return int(challenge) if challenge.isdigit() else challenge


@router.post("/whatsapp")
async def whatsapp_webhook(payload: dict):
    processed = []
    for message in parse_webhook_payload(payload):
        state = await run_lead_workflow(
            {
                "lead": {
                    "source": "whatsapp",
                    "customer_phone": message.from_number,
                    "message": message.text,
                    "details": {},
                    "conversation_history": [{"role": "customer", "content": message.text}],
                }
            }
        )
        processed.append(state)
    return {"status": "ok", "processed": len(processed)}


@router.post("/instagram")
async def instagram_webhook(payload: dict):
    client = get_instagram_client()
    processed = []
    for message in client.parse_webhook(payload):
        state = await run_lead_workflow(
            {
                "lead": {
                    "source": "instagram",
                    "customer_name": message["sender_id"],
                    "message": message["text"],
                    "details": {},
                    "conversation_history": [{"role": "customer", "content": message["text"]}],
                }
            }
        )
        processed.append(state)
    return {"status": "ok", "processed": len(processed)}


@router.post("/telegram")
async def telegram_webhook(payload: dict):
    bot = get_telegram_bot()
    data = bot.parse_webhook(payload)
    return {"status": "ok", "update": data}


@router.post("/form")
async def form_webhook(payload: FormSubmission):
    state = await run_lead_workflow(
        {
            "lead": {
                "business_id": payload.business_id,
                "source": "form",
                "customer_name": payload.name,
                "customer_phone": payload.phone,
                "customer_email": payload.email,
                "message": payload.message,
                "details": {"source_url": payload.source_url},
                "conversation_history": [{"role": "customer", "content": payload.message}],
            }
        }
    )
    return {"status": "ok", "state": state}


@router.post("/email")
async def email_webhook(payload: dict):
    state = await run_lead_workflow(
        {
            "lead": {
                "source": "email",
                "customer_name": payload.get("from_name"),
                "customer_email": payload.get("from_email"),
                "message": payload.get("body", ""),
                "details": {"subject": payload.get("subject")},
                "conversation_history": [{"role": "customer", "content": payload.get("body", "")}],
            }
        }
    )
    return {"status": "ok", "state": state}
