from app.agents.scoring.agent import ScoringAgent


import pytest


@pytest.mark.asyncio
async def test_scoring_agent_sets_score():
    state = {
        "lead": {"message": "Need catering for 100 guests this Saturday with budget 5000"},
        "research": {"legitimacy_score": 8.0},
    }
    agent = ScoringAgent()
    result = await agent.run(state)
    assert result["scoring"]["score"] >= 5
