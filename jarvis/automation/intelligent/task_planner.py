import logging
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Automation.Planner")

class TaskPlanner:
    """Converts natural language goals into execution graphs with retry boundaries and rollback steps."""

    def __init__(self):
        pass

    def generate_plan(self, goal: str) -> Dict[str, Any]:
        """Translates high-level prompt into a dependency graph containing atomic tasks."""
        logger.info(f"Planning task execution graph for goal: '{goal}'")
        
        goal_lower = goal.lower()
        subtasks = []
        
        if "powerpoint" in goal_lower or "ppt" in goal_lower:
            subtasks = [
                {"id": "t1", "action_type": "LAUNCH_APP", "app": "PowerPoint", "dependencies": [], "retry_limit": 2},
                {"id": "t2", "action_type": "CLICK_CONTROL", "target": "Blank Presentation", "dependencies": ["t1"], "retry_limit": 3},
                {"id": "t3", "action_type": "TYPE_TEXT", "target": "TitleBox", "text": "JARVIS AI OS", "dependencies": ["t2"], "retry_limit": 2},
                {"id": "t4", "action_type": "SHORTCUT", "key": "Ctrl+Shift+S", "dependencies": ["t3"], "retry_limit": 2},
                {"id": "t5", "action_type": "TYPE_TEXT", "target": "SaveDialogInput", "text": "JarvisPresentation.pptx", "dependencies": ["t4"], "retry_limit": 2},
                {"id": "t6", "action_type": "CLICK_CONTROL", "target": "Save", "dependencies": ["t5"], "retry_limit": 3}
            ]
        elif "workspace" in goal_lower or "development" in goal_lower:
            subtasks = [
                {"id": "t1", "action_type": "LAUNCH_APP", "app": "Code.exe", "dependencies": [], "retry_limit": 2},
                {"id": "t2", "action_type": "LAUNCH_APP", "app": "Terminal.exe", "dependencies": ["t1"], "retry_limit": 2},
                {"id": "t3", "action_type": "SHORTCUT", "key": "Ctrl+Shift+P", "dependencies": ["t2"], "retry_limit": 2}
            ]
        else:
            subtasks = [
                {"id": "t1", "action_type": "LAUNCH_APP", "app": "Chrome.exe", "dependencies": [], "retry_limit": 2},
                {"id": "t2", "action_type": "CLICK_CONTROL", "target": "SearchBar", "dependencies": ["t1"], "retry_limit": 3}
            ]
            
        plan = {
            "goal": goal,
            "subtasks": subtasks,
            "rollback_plan": {
                "t6": {"action_type": "SHORTCUT", "key": "Escape"},
                "t5": {"action_type": "SHORTCUT", "key": "Escape"}
            }
        }
        logger.info(f"Execution graph generated with {len(subtasks)} actions.")
        return plan
