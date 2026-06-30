import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Plugins.Context")

class PluginContext:
    """Manages active session data context variables for plugins."""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.variables: Dict[str, Any] = {}

    def set_variable(self, key: str, value: Any):
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)
