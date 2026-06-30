import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JARVIS.Distributed.Scheduler")

class DistributedScheduler:
    """Dispatches execution payloads on peer nodes optimized for resource usage (CPU/RAM)."""

    def __init__(self):
        pass

    def select_optimal_node(self, task: Dict[str, Any], active_nodes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Finds the node with highest capacity (CPU/RAM metrics)."""
        logger.info("Evaluating node resource metrics profiles to schedule task execution...")
        
        if not active_nodes:
            logger.info("No active cluster followers found. Scheduling task locally.")
            return None

        optimal = sorted(active_nodes, key=lambda n: n.get("cpu_cores", 1) * n.get("ram_mb", 1.0), reverse=True)[0]
        logger.info(f"Task scheduled on optimal cluster node: '{optimal['name']}' ({optimal['ip']})")
        return optimal
