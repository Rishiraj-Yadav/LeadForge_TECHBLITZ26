"""Outreach agent — crafts initial personalized response."""

from app.agents.base import BaseAgent
from app.agents.outreach.personalizer import generate_personalized_opening
from app.agents.outreach.templates import initial_message
from app.schemas.agent_state import AgentState


class OutreachAgent(BaseAgent):
    name = "outreach"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        opening = generate_personalized_opening(lead)
        reply = initial_message(opening, lead.get("message", ""))
        history = lead.setdefault("conversation_history", [])
        history.append({"role": "ai", "content": reply})
        state["lead"] = lead
        state["current_agent"] = self.name
        state["next_agent"] = "conversation"
        return state
