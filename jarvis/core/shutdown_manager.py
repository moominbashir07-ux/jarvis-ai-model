import logging
from typing import Dict, Any
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.runtime_database import RuntimeDatabase

logger = logging.getLogger("JARVIS.Core.Shutdown")

class ShutdownManager:
    """Manages graceful subsystem shutdown sequences, flushing contexts to SQLite."""

    def __init__(self, registry: ServiceRegistry, db: RuntimeDatabase):
        self.registry = registry
        self.db = db

    def execute_shutdown(self) -> bool:
        """Stops registered services, saves database sessions, and archives files."""
        logger.info("Executing Master graceful shutdown sequence...")
        
        try:
            services = ["AgentService", "AutomationService", "VoiceService", "VisionService", "MemoryService", "DatabaseService"]
            
            for svc in services:
                logger.info(f"Stopping subsystem service: '{svc}'")
                self.registry.disable_service(svc)
                self.db.log_lifecycle_event("SHUTDOWN_SERVICE", f"Shutdown service {svc}")

            logger.info("Master Graceful shutdown sequence successfully completed.")
            return True
        except Exception as e:
            logger.error(f"Shutdown sequence crashed: {e}")
            return False
