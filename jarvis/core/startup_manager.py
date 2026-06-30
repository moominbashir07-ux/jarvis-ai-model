import logging
from typing import Dict, Any, List
from jarvis.core.dependency_graph import DependencyGraph
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.runtime_database import RuntimeDatabase

logger = logging.getLogger("JARVIS.Core.Startup")

class StartupManager:
    """Manages boot sequences, initializing subsystems in topological dependency orders."""

    def __init__(self, registry: ServiceRegistry, db: RuntimeDatabase):
        self.registry = registry
        self.db = db
        self.dep_graph = DependencyGraph()
        self._configure_dependencies()

    def _configure_dependencies(self):
        self.dep_graph.add_service("DatabaseService", [])
        self.dep_graph.add_service("MemoryService", ["DatabaseService"])
        self.dep_graph.add_service("VisionService", ["MemoryService"])
        self.dep_graph.add_service("VoiceService", ["MemoryService"])
        self.dep_graph.add_service("AutomationService", ["VisionService"])
        self.dep_graph.add_service("AgentService", ["AutomationService"])

    def execute_boot(self) -> bool:
        """Runs the topological boot list, registering instances to lookup caching registries."""
        logger.info("Executing Master cold boot sequence...")
        
        try:
            boot_order = self.dep_graph.resolve_initialization_order()
            
            for svc in boot_order:
                logger.info(f"Booting subsystem service: '{svc}'")
                mock_instance = f"MockInstance_{svc}"
                self.registry.register_service(svc, mock_instance, status="running")
                self.db.log_lifecycle_event("BOOT_SERVICE", f"Booted service {svc}")

            logger.info("Master Boot sequence completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Cold boot sequence crashed: {e}")
            return False
