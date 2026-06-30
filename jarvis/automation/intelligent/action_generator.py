import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Automation.Action")

class ActionGenerator:
    """Formulates details for execution actions containing target tags, reasoning, and expected outcomes."""

    def __init__(self):
        pass

    def create_action(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Translates a subtask definition into a concrete executable action descriptor."""
        t_type = subtask["action_type"]
        
        action = {
            "id": subtask["id"],
            "type": t_type,
            "confidence": 0.95,
            "reason": f"Required task element for step: {subtask['id']}"
        }

        if t_type == "LAUNCH_APP":
            action["target"] = subtask["app"]
            action["expected_result"] = f"Application window '{subtask['app']}' is visible."
        elif t_type == "CLICK_CONTROL":
            action["target"] = subtask["target"]
            action["expected_result"] = f"Control element '{subtask['target']}' receives input focus."
        elif t_type == "TYPE_TEXT":
            action["target"] = subtask["target"]
            action["text"] = subtask["text"]
            action["expected_result"] = f"Value '{subtask['text']}' is entered into '{subtask['target']}'."
        elif t_type == "SHORTCUT":
            action["target"] = subtask["key"]
            action["expected_result"] = f"Hotkey sequence '{subtask['key']}' triggered."
        else:
            action["target"] = "None"
            action["expected_result"] = "None"
            
        logger.debug(f"Generated atomic action: {action}")
        return action
