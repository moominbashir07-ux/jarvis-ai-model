import queue
import time
import logging
import threading
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JARVIS.Agents.Scheduler")

class MultiAgentScheduler:
    """Manages thread-safe task prioritizing queue queues for dynamic agent dispatching."""

    def __init__(self):
        self._lock = threading.Lock()
        self.task_queue = queue.PriorityQueue()

    def schedule_task(self, priority: int, task: Dict[str, Any]):
        """Pushes a subtask configuration to the priority execution pool queue."""
        with self._lock:
            self.task_queue.put((priority, time.time(), task))
            logger.info(f"Task scheduled in priority queue: '{task['id']}' (Priority: {priority})")

    def pop_task(self) -> Optional[Dict[str, Any]]:
        """Pops the highest priority task available in queue."""
        with self._lock:
            if self.task_queue.empty():
                return None
            _, _, task = self.task_queue.get()
            return task
