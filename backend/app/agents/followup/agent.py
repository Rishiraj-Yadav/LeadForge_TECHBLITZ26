"""Follow-up agent — schedules next automated touchpoint."""

from datetime import datetime, timezone

from app.agents.base import BaseAgent
from app.agents.followup.scheduler import next_followup_time
from app.agents.followup.sequences import get_followup_message
from app.schemas.agent_state import AgentState


class FollowupAgent(BaseAgent):
    name = "followup"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        history = lead.setdefault("conversation_history", [])
        followup_attempt = sum(1 for item in history if item.get("role") == "ai_followup")
        scheduled = next_followup_time(datetime.now(timezone.utc), followup_attempt)
        history.append({"role": "ai_followup", "content": get_followup_message(followup_attempt)})
        state["lead"] = lead
        state["follow_up_scheduled"] = True
        state["next_followup"] = scheduled.isoformat()
        state["current_agent"] = self.name
        state["next_agent"] = "pipeline"
        return state
