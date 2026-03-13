"""Gemini-powered conversational capture service.

Uses Google Gemini to have natural multi-turn conversations with customers,
progressively extracting structured lead information without forms.
"""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.services.llm.factory import get_llm
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Fields we know how to extract across industries
FIELD_LABELS = {
    "guest_count": "Number of guests/people",
    "date": "Preferred date",
    "time": "Preferred time",
    "event_type": "Event or occasion type",
    "check_in": "Check-in date",
    "check_out": "Check-out date",
    "room_type": "Room type preference",
    "budget": "Budget or price range",
    "dietary_restrictions": "Dietary restrictions",
    "property_type": "Property type (apartment, house, etc.)",
    "location": "Preferred location or area",
    "bedrooms": "Number of bedrooms",
    "name": "Customer name",
    "phone": "Phone number",
    "email": "Email address",
}


class GeminiCaptureService:
    """Conversational AI that extracts lead data through natural dialog."""

    def __init__(self):
        self.llm = get_llm(temperature=0.4)

    async def process_message(
        self,
        message: str,
        *,
        business_name: str,
        business_industry: str,
        services_offered: str | None,
        capture_fields: dict[str, bool],
        captured_so_far: dict,
        conversation_history: list[dict],
    ) -> dict:
        """Generate a conversational reply and extract structured data.

        Returns:
            {
                "reply": str,          — natural response to send to customer
                "extracted_fields": dict,  — newly extracted key-value pairs
                "capture_complete": bool   — True when all required fields captured
            }
        """
        required = [k for k, v in capture_fields.items() if v]
        optional = [k for k, v in capture_fields.items() if not v]
        missing = [f for f in required if f not in captured_so_far or not captured_so_far[f]]

        # Build conversation context string
        history_text = ""
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            role = "Customer" if msg.get("role") == "customer" else "AI"
            history_text += f"{role}: {msg.get('content', '')}\n"

        field_descriptions = ", ".join(
            f"{k} ({FIELD_LABELS.get(k, k)})" for k in required
        )
        optional_descriptions = ", ".join(
            f"{k} ({FIELD_LABELS.get(k, k)})" for k in optional
        ) if optional else "none"
        captured_text = json.dumps(captured_so_far, indent=2) if captured_so_far else "Nothing yet"

        system_prompt = f"""You are a friendly, professional AI assistant for "{business_name}" ({business_industry}).
{f"Services: {services_offered}" if services_offered else ""}

Your job is to have a natural conversation with the customer, answer their questions helpfully, and progressively gather the information we need.

REQUIRED fields to capture: {field_descriptions}
OPTIONAL fields (ask only if natural): {optional_descriptions}
Already captured: {captured_text}
Still missing (required): {", ".join(missing) if missing else "ALL CAPTURED"}

RULES:
1. Be warm, helpful, and conversational — NOT robotic
2. Answer the customer's actual question FIRST, then naturally transition to the next question
3. Ask only ONE question at a time
4. Extract any information the customer already provided in their message
5. Use emojis sparingly for a friendly tone
6. Keep responses concise (2-4 sentences max)
7. If all required fields are captured, confirm the details and let them know someone will be in touch soon

Previous conversation:
{history_text}
Customer's latest message: "{message}"

Respond with ONLY valid JSON (no markdown, no code fences):
{{"reply": "your natural response", "extracted_fields": {{"field_name": "value"}}, "capture_complete": true/false}}

For extracted_fields, only include fields you can confidently extract from this message. Use these exact field names: {', '.join(required + optional)}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=message),
            ])
            return self._parse_response(response.content, missing)
        except Exception as exc:
            logger.error(f"Gemini capture error: {exc}")
            # Fallback: send a generic response
            if missing:
                field_label = FIELD_LABELS.get(missing[0], missing[0])
                return {
                    "reply": f"Thanks for reaching out! Could you let me know your {field_label.lower()}?",
                    "extracted_fields": {},
                    "capture_complete": False,
                }
            return {
                "reply": "Thanks for providing all that info! Someone from our team will be in touch shortly.",
                "extracted_fields": {},
                "capture_complete": True,
            }

    def _parse_response(self, raw: str, missing_fields: list[str]) -> dict:
        """Parse Gemini's JSON response, handling common format issues."""
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}

        reply = data.get("reply", "Thanks for your message! Let me help you with that.")
        extracted = data.get("extracted_fields", {})
        # Remove empty/null extracted fields
        extracted = {k: v for k, v in extracted.items() if v}

        capture_complete = data.get("capture_complete", False)
        # Double-check: if no missing fields remain after extraction, mark complete
        remaining = [f for f in missing_fields if f not in extracted]
        if not remaining and missing_fields:
            capture_complete = True

        return {
            "reply": reply,
            "extracted_fields": extracted,
            "capture_complete": capture_complete,
        }


def get_capture_service() -> GeminiCaptureService:
    return GeminiCaptureService()
