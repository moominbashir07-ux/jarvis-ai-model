import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Runtime.Session")

class SessionManager:
    """Manages active dialogue session variables and telemetry logs contexts."""

    def __init__(self):
        self.session_variables: Dict[str, Any] = {
            "conversation_id": "session_e2e_1",
            "active_nodes_count": 1,
            "current_user": "Owner"
        }

    def set_var(self, key: str, value: Any):
        self.session_variables[key] = value
        logger.debug(f"Session var updated: '{key}' => '{value}'")

    def get_var(self, key: str, default: Any = None) -> Any:
        return self.session_variables.get(key, default)
