import logging
from typing import Dict, Any
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Scheduler")

class SchedulerAgent(BaseAgent):
    """Autonomous Scheduler Agent for JARVIS AI OS.
    
    Coordinates calendar dates, time alarms, and schedules background worker tasks.
    """

    def __init__(self, task_queue=None):
        super().__init__(
            name="SchedulerAgent",
            description="Coordinates alarms, triggers, and scheduled background tasks."
        )
        self.queue = task_queue
        self.schedules = []

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Scheduling request: '{task_description}'")
        
        # Simple extraction rules for delay/schedule: "schedule task in 5 seconds"
        delay_seconds = 5.0
        try:
            if "second" in task_description:
                # Find number
                words = task_description.split()
                for i, w in enumerate(words):
                    if "second" in w and i > 0:
                        delay_seconds = float(words[i-1])
        except Exception:
            pass

        target_task_desc = (context or {}).get("task_description", "Scheduled default check")
        
        # Simulate scheduling
        logger.info(f"Registered background schedule: '{target_task_desc}' to run in {delay_seconds} seconds.")
        
        # In a real system, you would spawn a timer or write to cron/database
        self.schedules.append({
            "task": target_task_desc,
            "delay": delay_seconds,
            "status": "active"
        })

        return {
            "success": True,
            "delay_configured": delay_seconds,
            "task_registered": target_task_desc,
            "schedule_count": len(self.schedules)
        }

    def cleanup(self):
        logger.debug("SchedulerAgent cleanup completed.")
