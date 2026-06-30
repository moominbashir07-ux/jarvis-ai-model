import logging
from typing import Dict, Any, List
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Planner")

class PlannerAgent(BaseAgent):
    """Generates structured plans breaking high-level requests into ordered subtasks."""

    def __init__(self):
        super().__init__(
            name="PlannerAgent",
            description="Decomposes user requests into execution plans with dependency graphs."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Generating execution plan for: '{task_description}'")
        
        query_lower = task_description.lower()
        subtasks = []

        if "chips" in query_lower and "summarize" in query_lower:
            subtasks = [
                {
                    "task_id": "research_chips",
                    "description": "Research the latest AI computer chips.",
                    "target_agent": "researchagent",
                    "dependencies": [],
                    "status": "PENDING"
                },
                {
                    "task_id": "write_summary",
                    "description": "Create a summary text file of the AI chips research.",
                    "target_agent": "automationagent",
                    "dependencies": ["research_chips"],
                    "status": "PENDING"
                },
                {
                    "task_id": "locate_save",
                    "description": "Locate the Save button on screen.",
                    "target_agent": "visionagent",
                    "dependencies": ["write_summary"],
                    "status": "PENDING"
                }
            ]
        elif "chrome" in query_lower or "weather" in query_lower:
            subtasks = [
                {
                    "task_id": "open_browser",
                    "description": "Launch weather website.",
                    "target_agent": "automationagent",
                    "dependencies": [],
                    "status": "PENDING"
                },
                {
                    "task_id": "say_forecast",
                    "description": "Say forecast results aloud.",
                    "target_agent": "conversationagent",
                    "dependencies": ["open_browser"],
                    "status": "PENDING"
                }
            ]
        else:
            subtasks = [
                {
                    "task_id": "generic_task",
                    "description": task_description,
                    "target_agent": "researchagent",
                    "dependencies": [],
                    "status": "PENDING"
                }
            ]

        plan = {
            "query": task_description,
            "subtasks": subtasks,
            "estimated_cost": 0.01,
            "required_tools": [sub["target_agent"] for sub in subtasks]
        }
        return {"success": True, "plan": plan}
