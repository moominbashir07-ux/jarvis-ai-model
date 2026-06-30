import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Cognition.Goal")

class GoalManager:
    """Manages tracking status labels for current, completed, and blocked goals."""

    def __init__(self):
        self.goals: Dict[str, Dict[str, Any]] = {}

    def add_goal(self, goal_id: str, desc: str, status: str = "active"):
        self.goals[goal_id] = {"description": desc, "status": status}
        logger.info(f"Goal added: [{goal_id}] '{desc}' ({status})")

    def update_goal_status(self, goal_id: str, status: str):
        if goal_id in self.goals:
            self.goals[goal_id]["status"] = status
            logger.info(f"Goal [{goal_id}] status updated to: '{status}'")
