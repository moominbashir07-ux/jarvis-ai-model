import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Core.StateManager")

class GlobalStateManager:
    """Manages central state parameters like voice status, running workflows, and foreground apps."""

    def __init__(self):
        self.state: Dict[str, Any] = {
            "voice_pipeline_active": False,
            "automation_active": False,
            "foreground_app": "System",
            "active_task": "Idle",
            "loaded_plugins_count": 0
        }

    def update_state(self, key: str, value: Any):
        self.state[key] = value
        logger.debug(f"Global State updated: '{key}' => '{value}'")

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
