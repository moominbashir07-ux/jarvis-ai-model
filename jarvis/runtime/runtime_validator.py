import logging
from typing import Dict, Any
from jarvis.core.service_registry import ServiceRegistry

logger = logging.getLogger("JARVIS.Runtime.Validator")

class RuntimeValidator:
    """Runs assertions confirming that all subsystems are responsive and running."""

    def __init__(self, registry: ServiceRegistry):
        self.registry = registry

    def validate_runtime_integrity(self) -> bool:
        logger.info("Executing E2E runtime integrity validation assertions...")
        
        required = ["Database", "Memory", "Voice", "Vision", "Cognition", "MultiAgent", "Distributed", "Automation", "Orchestrator"]
        for req in required:
            status = self.registry.get_service_status(req)
            if status != "running":
                logger.error(f"Integrity validation failed: service '{req}' is not in running state (current: '{status}')")
                return False
                
        logger.info("E2E runtime integrity validation completed successfully.")
        return True
