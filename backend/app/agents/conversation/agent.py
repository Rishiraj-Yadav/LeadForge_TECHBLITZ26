"""Conversation agent — classifies intent and prepares next routing."""

from app.agents.base import BaseAgent
from app.agents.conversation.intent_classifier import classify_intent
from app.agents.conversation.knowledge_base import answer_common_question
from app.schemas.agent_state import AgentState


class ConversationAgent(BaseAgent):
    name = "conversation"

    async def run(self, state: AgentState) -> AgentState:
        lead = state.get("lead", {})
        message = lead.get("message", "")
        intent = classify_intent(message)
        state["intent"] = intent
        state["sentiment"] = 0.8 if "thank" in message.lower() else 0.5

        faq_answer = answer_common_question(message)
        if faq_answer:
            lead.setdefault("conversation_history", []).append({"role": "ai", "content": faq_answer})
            state["lead"] = lead

        if intent == "needs_call":
            state["next_agent"] = "voice"
        elif intent == "ready_to_buy":
            state["next_agent"] = "pipeline"
        else:
            state["next_agent"] = "followup"

        state["current_agent"] = self.name
        return state
