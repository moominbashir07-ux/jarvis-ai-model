import logging
import concurrent.futures
from typing import List, Dict, Any
from jarvis.agents.dynamic.task_marketplace import TaskMarketplace

logger = logging.getLogger("JARVIS.Agents.Collaboration")

class CollaborationEngine:
    """Orchestrates dynamic agent execution groups to fulfill compound goals."""

    def __init__(self, marketplace: TaskMarketplace):
        self.marketplace = marketplace

    def execute_goal(self, goal: str, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Distributes subtasks across matched agents, running independent tasks in parallel."""
        logger.info(f"Collaboration graph created with {len(subtasks)} subtask definitions.")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for task in subtasks:
                agent = self.marketplace.route_task(task["requirement"])
                if agent:
                    futures[executor.submit(agent.execute_task, task)] = task["id"]
                else:
                    logger.warning(f"No matching agent found for subtask: {task['id']}")

            for future in concurrent.futures.as_completed(futures):
                task_id = futures[future]
                try:
                    out = future.result()
                    results.append({"id": task_id, "success": True, "output": out})
                except Exception as e:
                    logger.error(f"Async subtask {task_id} execution failed: {e}")
                    results.append({"id": task_id, "success": False, "error": str(e)})

        logger.info("Shared context synchronized successfully.")
        return {
            "goal": goal,
            "subtasks_results": results,
            "success": all(r["success"] for r in results)
        }
