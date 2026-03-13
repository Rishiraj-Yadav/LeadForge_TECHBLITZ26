"""Base agent abstraction."""

from abc import ABC, abstractmethod
from app.schemas.agent_state import AgentState


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, state: AgentState) -> AgentState:
        raise NotImplementedError
