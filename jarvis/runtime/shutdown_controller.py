import logging
from typing import Dict, Any
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.runtime_database import RuntimeDatabase

logger = logging.getLogger("JARVIS.Runtime.Shutdown")

class ShutdownController:
    """Manages cleanup tasks, flushing database records, and deactivating registered services."""

    def __init__(self, registry: ServiceRegistry, db: RuntimeDatabase):
        self.registry = registry
        self.db = db

    def execute_shutdown(self) -> bool:
        logger.info("Executing graceful cleanup sequence...")
        
        services = ["Orchestrator", "Automation", "Distributed", "MultiAgent", "Cognition", "Vision", "Voice", "Memory", "Database"]
        for svc in services:
            logger.info(f"Stopping service module: '{svc}'")
            self.registry.disable_service(svc)
            self.db.log_lifecycle_event("RUNTIME_SHUTDOWN", f"Stopped {svc}")
            
        logger.info("Cleanup sequence completed successfully.")
        return True
