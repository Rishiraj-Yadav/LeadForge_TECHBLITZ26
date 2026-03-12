"""LangGraph orchestration for the 9-agent LeadForge workflow."""

from langgraph.graph import StateGraph, END

from app.schemas.agent_state import AgentState
from app.agents.intake.agent import IntakeAgent
from app.agents.research.agent import ResearchAgent
from app.agents.scoring.agent import ScoringAgent
from app.agents.notification.agent import NotificationAgent
from app.agents.outreach.agent import OutreachAgent
from app.agents.conversation.agent import ConversationAgent
from app.agents.followup.agent import FollowupAgent
from app.agents.voice.agent import VoiceAgent
from app.agents.pipeline.agent import PipelineAgent


intake_agent = IntakeAgent()
research_agent = ResearchAgent()
scoring_agent = ScoringAgent()
notification_agent = NotificationAgent()
outreach_agent = OutreachAgent()
conversation_agent = ConversationAgent()
followup_agent = FollowupAgent()
voice_agent = VoiceAgent()
pipeline_agent = PipelineAgent()


async def intake_node(state: AgentState) -> AgentState:
    return await intake_agent.run(state)


async def research_node(state: AgentState) -> AgentState:
    return await research_agent.run(state)


async def scoring_node(state: AgentState) -> AgentState:
    return await scoring_agent.run(state)


async def notification_node(state: AgentState) -> AgentState:
    return await notification_agent.run(state)


async def outreach_node(state: AgentState) -> AgentState:
    return await outreach_agent.run(state)


async def conversation_node(state: AgentState) -> AgentState:
    return await conversation_agent.run(state)


async def followup_node(state: AgentState) -> AgentState:
    return await followup_agent.run(state)


async def voice_node(state: AgentState) -> AgentState:
    return await voice_agent.run(state)


async def pipeline_node(state: AgentState) -> AgentState:
    return await pipeline_agent.run(state)


def route_after_notification(state: AgentState) -> str:
    return state.get("next_agent", "wait_approval")


def route_after_conversation(state: AgentState) -> str:
    return state.get("next_agent", "followup")


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intake", intake_node)
    graph.add_node("research", research_node)
    graph.add_node("scoring", scoring_node)
    graph.add_node("notification", notification_node)
    graph.add_node("outreach", outreach_node)
    graph.add_node("conversation", conversation_node)
    graph.add_node("followup", followup_node)
    graph.add_node("voice", voice_node)
    graph.add_node("pipeline", pipeline_node)
    graph.add_node("wait_approval", lambda state: state)

    graph.set_entry_point("intake")

    graph.add_edge("intake", "research")
    graph.add_edge("research", "scoring")
    graph.add_edge("scoring", "notification")

    graph.add_conditional_edges(
        "notification",
        route_after_notification,
        {
            "outreach": "outreach",
            "pipeline": "pipeline",
            "wait_approval": "wait_approval",
        },
    )

    graph.add_edge("outreach", "conversation")

    graph.add_conditional_edges(
        "conversation",
        route_after_conversation,
        {
            "followup": "followup",
            "voice": "voice",
            "pipeline": "pipeline",
        },
    )

    graph.add_edge("followup", "pipeline")
    graph.add_edge("voice", "pipeline")
    graph.add_edge("pipeline", END)
    graph.add_edge("wait_approval", END)

    return graph.compile()


lead_graph = build_graph()


async def run_lead_workflow(initial_state: AgentState) -> AgentState:
    return await lead_graph.ainvoke(initial_state)
