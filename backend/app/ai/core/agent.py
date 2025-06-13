"""Base agent implementation."""

from abc import ABC, abstractmethod
from typing import Any

from app.ai.core.config import AIConfig


class Agent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, config: AIConfig):
        """Initialize the agent.

        Args:
            config: AI configuration settings
        """
        self.config = config

    @abstractmethod
    async def process(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Process the input and generate a response.

        Args:
            inputs: Input data for processing

        Returns:
            Processing results
        """
        pass
