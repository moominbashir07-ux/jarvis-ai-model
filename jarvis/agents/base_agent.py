import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Agents")

class BaseAgent(ABC):
    """Abstract base class that all task-specific JARVIS sub-agents inherit from."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        logger.debug(f"Sub-agent '{self.name}' initialized: {self.description}")

    def initialize(self):
        """Initializes internal sub-agent mechanisms/tools."""
        logger.info(f"Starting sub-agent: [{self.name}]")

    @abstractmethod
    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executes a specialized task.
        
        Args:
            task_description: Plain text goal prompt.
            context: Supplemental context data.
            
        Returns:
            Dict containing result status, output values, or logs.
        """
        pass

    def cleanup(self):
        """Clean up sub-agent execution handles."""
        logger.debug(f"Sub-agent [{self.name}] cleanup complete.")
class FakeSearchAgent(BaseAgent):
    """Mock example showing how a specialized agent inherits from BaseAgent."""

    def __init__(self):
        super().__init__(
            name="SearchAgent",
            description="Searches directories and local files for specific content."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Agent [{self.name}] searching: '{task_description}'")
        return {"success": True, "results": ["file1.txt", "file2.log"]}
