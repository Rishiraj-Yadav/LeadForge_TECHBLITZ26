"""Intake agent — normalizes inbound leads."""

from app.agents.base import BaseAgent
from app.schemas.agent_state import AgentState


class IntakeAgent(BaseAgent):
    name = "intake"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        lead.setdefault("details", {})
        lead.setdefault("conversation_history", [])
        state["lead"] = lead
        state["current_agent"] = self.name
        state["next_agent"] = "research"
        return state
