"""Voice agent — decides human transfer or call continuation."""

from app.agents.base import BaseAgent
from app.agents.voice.call_flow import should_transfer_to_human
from app.schemas.agent_state import AgentState


class VoiceAgent(BaseAgent):
    name = "voice"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        transcript = lead.get("message", "")
        state["should_escalate"] = should_transfer_to_human(transcript)
        state["current_agent"] = self.name
        state["next_agent"] = "pipeline"
        return state
