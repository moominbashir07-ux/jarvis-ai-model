import logging
from typing import List, Dict, Any
from jarvis.agents.dynamic.agent_factory import DynamicAgentInstance

logger = logging.getLogger("JARVIS.Agents.Optimizer")

class AgentOptimizer:
    """Monitors dynamic agent latencies, CPU footprints, and optimization targets."""

    def __init__(self, slow_threshold_seconds: float = 1.0):
        self.slow_threshold = slow_threshold_seconds

    def optimize_agent_pool(self, agents: List[DynamicAgentInstance]) -> List[Dict[str, Any]]:
        """Audits latency lists and yields optimization recommendations for bottleneck agents."""
        logger.info("Running agent resource allocation optimization audit...")
        recommendations = []

        for agent in agents:
            if not agent.latency_history:
                continue
            avg_lat = sum(agent.latency_history) / len(agent.latency_history)
            
            if avg_lat > self.slow_threshold:
                logger.warning(f"Agent '{agent.name}' exhibits high execution latency: {avg_lat:.2f}s!")
                recommendations.append({
                    "agent_name": agent.name,
                    "avg_latency": avg_lat,
                    "recommendation": "Increase CPU priority index and spin up parallel clones."
                })

        logger.info("Agent optimization complete.")
        return recommendations
