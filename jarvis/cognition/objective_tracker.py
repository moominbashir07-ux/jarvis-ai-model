import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Cognition.Tracker")

class ObjectiveTracker:
    """Classifies goals status timelines into daily, weekly, or long-term schedules."""

    def __init__(self):
        self.schedules: Dict[str, List[str]] = {
            "daily": [],
            "weekly": [],
            "long_term": []
        }

    def assign_objective_schedule(self, goal_id: str, term: str):
        if term in self.schedules:
            self.schedules[term].append(goal_id)
            logger.info(f"Assigned objective [{goal_id}] to '{term}' tracking timeline schedule.")
