import logging
from typing import Dict, Any, List
from jarvis.core.dependency_graph import DependencyGraph
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.runtime_database import RuntimeDatabase

logger = logging.getLogger("JARVIS.Runtime.Initializer")

class ServiceInitializer:
    """Orchestrates sequential startup procedures for all modular packages."""

    def __init__(self, registry: ServiceRegistry, db: RuntimeDatabase):
        self.registry = registry
        self.db = db
        self.graph = DependencyGraph()
        self._configure_dependencies()

    def _configure_dependencies(self):
        self.graph.add_service("Database", [])
        self.graph.add_service("Memory", ["Database"])
        self.graph.add_service("Voice", ["Memory"])
        self.graph.add_service("Vision", ["Memory"])
        self.graph.add_service("Cognition", ["Memory"])
        self.graph.add_service("MultiAgent", ["Cognition"])
        self.graph.add_service("Distributed", ["Database"])
        self.graph.add_service("Automation", ["Vision"])
        self.graph.add_service("Orchestrator", ["Database", "Memory"])

    def boot_all_services(self) -> bool:
        logger.info("Initializing runtime startup sequence...")
        try:
            boot_order = self.graph.resolve_initialization_order()
            for svc in boot_order:
                logger.info(f"Initializing runtime service module: '{svc}'")
                mock_instance = f"RuntimeInstance_{svc}"
                self.registry.register_service(svc, mock_instance, status="running")
                self.db.log_lifecycle_event("RUNTIME_BOOT", f"Initialized {svc}")
                
            logger.info("All runtime service modules successfully initialized.")
            return True
        except Exception as e:
            logger.error(f"Runtime boots sequence failed: {e}")
            return False
