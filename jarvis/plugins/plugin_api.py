import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Plugins.API")

class PluginAPI:
    """Safe gateway exposing core JARVIS endpoints to plugins."""

    def __init__(self, plugin_id: str, permissions: Any):
        self.plugin_id = plugin_id
        self.permissions = permissions

    def log_message(self, message: str):
        """Allows plugins to write logs."""
        logger.info(f"[{self.plugin_id}] {message}")

    def trigger_notification(self, title: str, text: str) -> bool:
        """Sends a notification popup if the plugin has 'notifications' permissions."""
        if not self.permissions.verify_permission(self.plugin_id, "notifications"):
            logger.warning(f"Notification request blocked for plugin: '{self.plugin_id}'")
            return False
            
        logger.info(f"Triggering Notification: [{title}] {text}")
        return True

    def read_local_file(self, file_path: str) -> str:
        """Reads file contents if the plugin has 'filesystem_read' permissions."""
        if not self.permissions.verify_permission(self.plugin_id, "filesystem_read"):
            raise PermissionError(f"Plugin '{self.plugin_id}' is not authorized to read files.")
            
        logger.info(f"Plugin reading file: '{file_path}'")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
