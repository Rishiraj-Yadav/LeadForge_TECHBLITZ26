"""Notification agent — alerts rep and applies score routing."""

from app.agents.base import BaseAgent
from app.agents.notification.formatters import format_rep_summary
from app.agents.notification.templates import APPROVAL_BUTTONS
from app.schemas.agent_state import AgentState
from app.services.telegram.bot import get_telegram_bot
from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class NotificationAgent(BaseAgent):
    name = "notification"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        research = state.get("research", {})
        scoring = state.get("scoring", {})
        score = float(scoring.get("score", 0))
        summary = format_rep_summary(lead, research, scoring)
        lead_id = lead.get("id", "")

        if score < 5:
            state["rep_decision"] = "rejected"
            state["next_agent"] = "pipeline"
            return state

        # Determine which chat to notify: per-business or global fallback
        rep_chat_id = (
            lead.get("business_telegram_chat_id")
            or settings.REP_TELEGRAM_CHAT_ID
        )

        try:
            if rep_chat_id:
                telegram = get_telegram_bot()
                await telegram.send_inline_keyboard(
                    str(rep_chat_id),
                    summary,
                    [
                        [
                            {"text": APPROVAL_BUTTONS[0]["title"], "callback_data": f"approve:{lead_id}"},
                            {"text": APPROVAL_BUTTONS[1]["title"], "callback_data": f"reject:{lead_id}"},
                        ],
                        [
                            {"text": APPROVAL_BUTTONS[2]["title"], "callback_data": f"view_chat:{lead_id}"},
                        ],
                    ],
                )
                logger.info(f"Notification sent to {rep_chat_id} for lead {lead_id[:8]}...")
        except Exception as exc:
            logger.error(f"Failed to send notification: {exc}")

        state["rep_decision"] = "approved" if score > 7 else state.get("rep_decision", "pending")
        state["current_agent"] = self.name
        state["next_agent"] = "outreach" if state["rep_decision"] == "approved" else "wait_approval"
        return state
