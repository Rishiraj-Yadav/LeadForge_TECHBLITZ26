"""Voice handling endpoints for Twilio webhooks."""

from fastapi import APIRouter, Form, Response

from app.services.twilio.voice import get_voice_service

router = APIRouter()


@router.post("/incoming")
async def incoming_call():
    service = get_voice_service()
    xml = service.create_inbound_twiml("wss://your-domain.com/ws/voice")
    return Response(content=xml, media_type="application/xml")


@router.post("/gather")
async def gather_speech(SpeechResult: str = Form(default="")):
    service = get_voice_service()
    if "human" in SpeechResult.lower():
        xml = service.transfer_to_rep("+10000000000")
    else:
        xml = service.create_gather_twiml(
            "Thanks. Could you tell me a little more about what you need?",
            "/api/v1/voice/gather",
        )
    return Response(content=xml, media_type="application/xml")
