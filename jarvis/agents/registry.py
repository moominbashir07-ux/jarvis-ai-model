import logging
from typing import Dict, Optional
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Registry")

class AgentRegistry:
    """Registry directory storing active JARVIS agent instances to support agent collaboration."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        logger.debug("AgentRegistry instance created.")

    def register_agent(self, agent: BaseAgent):
        """Adds an agent instance to the lookup registry directory."""
        self.agents[agent.name.lower()] = agent
        logger.info(f"Registered Agent: [{agent.name}]")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Looks up an active agent instance by name (case-insensitive)."""
        return self.agents.get(name.lower())

    def clear(self):
        """Cleans up all registered agent allocations."""
        self.agents.clear()

# Global Singleton registry instance
agent_registry = AgentRegistry()
