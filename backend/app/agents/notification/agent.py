"""Notification agent — alerts rep and applies score routing."""

from app.agents.base import BaseAgent
from app.agents.notification.formatters import format_rep_summary
from app.agents.notification.templates import APPROVAL_BUTTONS
from app.schemas.agent_state import AgentState
from app.services.telegram.bot import get_telegram_bot
from app.services.whatsapp.client import get_whatsapp_client
from app.config import get_settings

settings = get_settings()


class NotificationAgent(BaseAgent):
    name = "notification"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        research = state.get("research", {})
        scoring = state.get("scoring", {})
        score = float(scoring.get("score", 0))
        summary = format_rep_summary(lead, research, scoring)

        if score < 5:
            state["rep_decision"] = "rejected"
            state["next_agent"] = "pipeline"
            return state

        try:
            whatsapp = get_whatsapp_client()
            if settings.REP_WHATSAPP_NUMBER:
                await whatsapp.send_interactive_buttons(
                    settings.REP_WHATSAPP_NUMBER,
                    summary,
                    APPROVAL_BUTTONS,
                )
        except Exception:
            pass

        try:
            telegram = get_telegram_bot()
            if settings.REP_TELEGRAM_CHAT_ID:
                await telegram.send_inline_keyboard(
                    settings.REP_TELEGRAM_CHAT_ID,
                    summary,
                    [[
                        {"text": "Approve", "callback_data": "approve"},
                        {"text": "Reject", "callback_data": "reject"},
                    ]],
                )
        except Exception:
            pass

        state["rep_decision"] = "approved" if score > 7 else state.get("rep_decision", "pending")
        state["current_agent"] = self.name
        state["next_agent"] = "outreach" if state["rep_decision"] == "approved" else "wait_approval"
        return state
