"""Base tool interface for ReAct pattern."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Base class for ReAct tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for the LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters(),
        }

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool."""
        pass
