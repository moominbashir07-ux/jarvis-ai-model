import logging
import time
from typing import Dict, Any, List
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Supervisor")

class SupervisorAgent(BaseAgent):
    """Monitors the autonomous execution thread, preventing deadlocks or infinite loops."""

    def __init__(self, max_retries: int = 2, max_runtime_seconds: float = 60.0):
        super().__init__(
            name="SupervisorAgent",
            description="Supervises execution graphs, enforcing timeouts and stall checks."
        )
        self.max_retries = max_retries
        self.max_runtime = max_runtime_seconds
        
        self._failure_counts: Dict[str, int] = {}
        self._start_times: Dict[str, float] = {}

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"SupervisorAgent reviewing task pipeline status: '{task_description}'")
        context = context or {}
        task_id = context.get("task_id", "default")
        status = context.get("status")

        if status == "START":
            self._start_times[task_id] = time.time()
            return {"success": True, "action": "CONTINUE"}

        if task_id in self._start_times:
            elapsed = time.time() - self._start_times[task_id]
            if elapsed > self.max_runtime:
                logger.critical(f"Task {task_id} TIMED OUT after {elapsed:.1f}s (Max: {self.max_runtime}s)!")
                return {"success": True, "action": "ABORT", "reason": "EXECUTION_TIMEOUT"}

        if status == "FAILED":
            count = self._failure_counts.get(task_id, 0) + 1
            self._failure_counts[task_id] = count
            logger.warning(f"Task {task_id} failed. Consecutive failures: {count}/{self.max_retries}")
            
            if count >= self.max_retries:
                logger.critical(f"Task {task_id} exceeded maximum retries of {self.max_retries}!")
                return {"success": True, "action": "REPLAN", "reason": "RETRY_LIMIT_EXCEEDED"}
            return {"success": True, "action": "RETRY"}

        return {"success": True, "action": "CONTINUE"}
