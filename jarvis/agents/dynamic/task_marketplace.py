import logging
from typing import List, Dict, Any, Optional
from jarvis.agents.dynamic.agent_factory import DynamicAgentInstance

logger = logging.getLogger("JARVIS.Agents.Marketplace")

class TaskMarketplace:
    """Matches task requirements to optimal dynamic agent instances using capability filters."""

    def __init__(self):
        self.registered_agents: List[DynamicAgentInstance] = []

    def join_marketplace(self, agent: DynamicAgentInstance):
        """Adds an active agent to the marketplace pool."""
        self.registered_agents.append(agent)
        logger.debug(f"Agent '{agent.name}' joined the task marketplace.")

    def leave_marketplace(self, agent_name: str):
        """Removes an active agent from the marketplace pool."""
        self.registered_agents = [a for a in self.registered_agents if a.name != agent_name]
        logger.debug(f"Agent '{agent_name}' left the task marketplace.")

    def route_task(self, requirement: str) -> Optional[DynamicAgentInstance]:
        """Identifies which registered agent has the highest capability score match for the requirement."""
        logger.info(f"Routing subtask requirement: '{requirement}'")
        
        req_lower = requirement.lower()
        best_agent = None
        best_score = -1

        for agent in self.registered_agents:
            score = 0
            for cap in agent.capabilities:
                if cap.lower() in req_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_agent = agent

        if not best_agent and self.registered_agents:
            best_agent = self.registered_agents[0]
            
        if best_agent:
            logger.info(f"Routed to optimal agent: '{best_agent.name}' (Match score: {best_score})")
        else:
            logger.warning("No available dynamic agents registered in marketplace!")
            
        return best_agent
