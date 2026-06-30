import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Runtime.Router")

class RequestRouter:
    """Dispatches reasoning payloads based on complexity thresholds and node profiles."""

    def __init__(self):
        pass

    def route_request(self, command: str, complexity: str) -> str:
        logger.info(f"Routing request '{command}' with complexity: '{complexity}'")
        
        if complexity == "HIGH":
            target = "cloud_worker"
        elif complexity == "MEDIUM":
            target = "distributed_node"
        else:
            target = "local_executor"
            
        logger.info(f"Request successfully routed to target: '{target}'")
        return target
