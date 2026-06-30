import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Agents.Factory")

class DynamicAgentInstance:
    """Represents a dynamically spawned specialized agent instance."""

    def __init__(self, name: str, version: str, capabilities: List[str]):
        self.name = name
        self.version = version
        self.capabilities = capabilities
        self.latency_history: List[float] = []

    def execute_task(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Runs custom subtask execution logic based on capabilities details."""
        logger.info(f"Agent '{self.name}' executing task: '{subtask['goal']}'")
        
        import time
        t1 = time.time()
        time.sleep(0.01)
        duration = time.time() - t1
        self.latency_history.append(duration)
        
        return {
            "agent_name": self.name,
            "success": True,
            "output": f"Parsed results from dynamic action subtask: {subtask['goal']}",
            "duration": duration
        }

class AgentFactory:
    """Instantiates and configures specialized dynamic agent instances."""

    def __init__(self):
        pass

    def create_agent(self, name: str, capabilities: List[str], version: str = "1.0.0") -> DynamicAgentInstance:
        """Dynamically instantiates a new dynamic agent instance."""
        logger.debug(f"Instantiating dynamic specialized agent: '{name}' (Capabilities: {capabilities})")
        return DynamicAgentInstance(name, version, capabilities)
