import logging
import queue
import threading
import time
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger("JARVIS.Agents.TaskQueue")

class AgentTask:
    """Represents an autonomous task dispatched to an agent."""

    def __init__(
        self,
        task_id: str,
        description: str,
        target_agent: str,
        priority: str = "MEDIUM", # 'HIGH', 'MEDIUM', 'LOW'
        require_approval: bool = False,
        context: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.description = description
        self.target_agent = target_agent
        self.priority = priority.upper()
        self.require_approval = require_approval
        self.context = context or {}
        
        # States: 'PENDING', 'AWAITING_APPROVAL', 'APPROVED', 'RUNNING', 'COMPLETED', 'FAILED'
        self.status = "PENDING"
        self.result: Optional[Dict[str, Any]] = None

    def __lt__(self, other):
        # Priority mapping for queue comparison
        pri_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        return pri_map.get(self.priority, 1) < pri_map.get(other.priority, 1)


class AgentTaskQueue:
    """Prioritized background execution queue for JARVIS autonomous agents with human-in-the-loop approvals."""

    def __init__(self, approval_callback: Optional[Callable[[AgentTask], bool]] = None):
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.is_running = False
        self.worker_thread = None
        self.approval_handler = approval_callback or self._default_approval_prompt

    def start(self):
        """Starts the background worker queue consumer thread."""
        if self.is_running:
            return
        self.is_running = True
        self.worker_thread = threading.Thread(
            target=self._queue_worker_loop,
            daemon=True,
            name="JARVIS-Agent-QueueWorker"
        )
        self.worker_thread.start()
        logger.info("Agent prioritized task queue active in background.")

    def submit_task(self, task: AgentTask):
        """Pushes a task into the priority queue."""
        self.active_tasks[task.task_id] = task
        self.task_queue.put((task, task.task_id))
        logger.info(f"Submitted Task #{task.task_id} [{task.priority}] to Agent [{task.target_agent}].")

    def get_task_status(self, task_id: str) -> str:
        """Returns the execution state of a task."""
        task = self.active_tasks.get(task_id)
        return task.status if task else "UNKNOWN"

    def _queue_worker_loop(self):
        """Worker thread consumption loop."""
        # Dynamic local imports to resolve registry references
        from jarvis.agents.registry import agent_registry

        while self.is_running:
            try:
                # Wait for task (blocking for 0.5s to allow thread shutdown check)
                try:
                    task, task_id = self.task_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                logger.debug(f"Pulling Task #{task.task_id} from queue...")

                # 1. Human-in-the-loop safety verification check
                if task.require_approval:
                    task.status = "AWAITING_APPROVAL"
                    logger.warning(f"Task #{task.task_id} BLOCKED: Human approval required for safety.")
                    
                    approved = self.approval_handler(task)
                    if not approved:
                        logger.critical(f"Task #{task.task_id} REJECTED by user. Skipping execution.")
                        task.status = "FAILED"
                        task.result = {"error": "Rejected by human safety guardrail."}
                        self.task_queue.task_done()
                        continue
                    
                    logger.info(f"Task #{task.task_id} APPROVED. Continuing to execution.")
                    task.status = "APPROVED"

                # 2. Run agent execution pipeline
                task.status = "RUNNING"
                agent = agent_registry.get_agent(task.target_agent)
                
                if not agent:
                    logger.error(f"Target agent [{task.target_agent}] not found in registry.")
                    task.status = "FAILED"
                    task.result = {"error": f"Agent {task.target_agent} not found."}
                else:
                    try:
                        logger.info(f"Executing Task #{task.task_id} on Agent [{agent.name}]...")
                        result = agent.run(task.description, task.context)
                        task.status = "COMPLETED"
                        task.result = result
                    except Exception as e:
                        logger.error(f"Execution failed on Agent [{agent.name}] for Task #{task.task_id}: {e}")
                        task.status = "FAILED"
                        task.result = {"error": str(e)}

                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Error in task queue worker loop: {e}", exc_info=True)
                time.sleep(0.5)

    def _default_approval_prompt(self, task: AgentTask) -> bool:
        """Fallback approval simulator when no orchestrator GUI/Voice handler is bound."""
        # Simulated developer CLI approval check (default to True for non-blocking scripts)
        logger.info(f"Simulation Approval: Task #{task.task_id} description: '{task.description}'.")
        return True

    def stop(self):
        """Cleans up background worker threads."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        logger.debug("Agent task queue worker thread stopped.")
