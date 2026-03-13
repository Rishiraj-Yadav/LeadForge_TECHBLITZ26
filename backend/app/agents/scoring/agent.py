"""Scoring agent — combines heuristics and rules."""

from app.agents.base import BaseAgent
from app.agents.scoring.model import LeadScoringModel
from app.agents.scoring.rules import classify_urgency, score_reasoning
from app.schemas.agent_state import AgentState


class ScoringAgent(BaseAgent):
    name = "scoring"

    def __init__(self):
        self.model = LeadScoringModel()

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        research = state.get("research", {})
        message = lead.get("message", "")
        legitimacy = float(research.get("legitimacy_score", 5.0))

        prediction = self.model.predict(message, legitimacy)
        urgency = classify_urgency(message)
        reasoning = score_reasoning(prediction["score"], legitimacy, urgency)

        state["scoring"] = {
            "score": prediction["score"],
            "reasoning": reasoning,
            "urgency": urgency,
            "budget_indicators": prediction["budget_indicators"],
        }
        state["current_agent"] = self.name
        state["next_agent"] = "notification"
        return state
