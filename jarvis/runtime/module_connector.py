import logging
from typing import Dict, Any
from jarvis.core.service_registry import ServiceRegistry

logger = logging.getLogger("JARVIS.Runtime.Connector")

class ModuleConnector:
    """Validates connectivity bindings across registered packages."""

    def __init__(self, registry: ServiceRegistry):
        self.registry = registry

    def verify_connections(self) -> bool:
        logger.info("Verifying connectivity references across service registry...")
        
        required = ["Database", "Memory", "Voice", "Vision", "Cognition", "MultiAgent", "Distributed", "Automation", "Orchestrator"]
        for req in required:
            ref = self.registry.lookup_service(req)
            if not ref:
                logger.error(f"Missing connectivity binding pointer for required service: '{req}'")
                return False
                
        logger.info("Registry connection references verified successfully.")
        return True
