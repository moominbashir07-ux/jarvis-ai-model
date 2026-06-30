import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Plugins.Permissions")

class PermissionManager:
    """Validates capabilities scopes request parameters before routing actions."""

    def __init__(self):
        self.granted_permissions: Dict[str, List[str]] = {}

    def grant_permissions(self, plugin_id: str, permissions: List[str]):
        """Sets the granted permissions scope for a plugin."""
        self.granted_permissions[plugin_id] = [p.lower().strip() for p in permissions]
        logger.debug(f"Granted permissions to [{plugin_id}]: {self.granted_permissions[plugin_id]}")

    def verify_permission(self, plugin_id: str, permission: str) -> bool:
        """Verifies if the plugin has the requested permission granted."""
        granted = self.granted_permissions.get(plugin_id, [])
        req = permission.lower().strip()
        if req in granted:
            logger.debug(f"Permission verification SUCCESS: [{plugin_id}] has '{req}'")
            return True
        logger.warning(f"Permission verification FAILED: [{plugin_id}] requested '{req}' (Not granted!)")
        return False
