import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JARVIS.Core.Registry")

class ServiceRegistry:
    """Central lookup registry caching active instances of all running JARVIS subsystems."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._statuses: Dict[str, str] = {}

    def register_service(self, name: str, instance: Any, status: str = "running"):
        self._services[name] = instance
        self._statuses[name] = status
        logger.debug(f"Service registered in core registry: '{name}'")

    def lookup_service(self, name: str) -> Optional[Any]:
        return self._services.get(name)

    def disable_service(self, name: str):
        if name in self._statuses:
            self._statuses[name] = "disabled"
            logger.info(f"Deactivated service: '{name}'")

    def enable_service(self, name: str):
        if name in self._statuses:
            self._statuses[name] = "running"
            logger.info(f"Activated service: '{name}'")

    def get_service_status(self, name: str) -> Optional[str]:
        return self._statuses.get(name)
