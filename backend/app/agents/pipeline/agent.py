"""Pipeline agent — final stage selection and analytics."""

from app.agents.base import BaseAgent
from app.agents.pipeline.stage_manager import determine_stage
from app.agents.pipeline.analytics import close_probability
from app.schemas.agent_state import AgentState


class PipelineAgent(BaseAgent):
    name = "pipeline"

    async def run(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "qualification")
        rep_decision = state.get("rep_decision", "approved")
        score = float(state.get("scoring", {}).get("score", 0))
        stage = determine_stage(intent, rep_decision)
        state["stage"] = stage
        state["pipeline"] = {
            "stage": stage,
            "close_probability": close_probability(score, stage),
        }
        state["current_agent"] = self.name
        state["next_agent"] = "close"
        return state
