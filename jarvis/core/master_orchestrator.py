import logging
from typing import Dict, Any, List
from jarvis.core.lifecycle import RuntimeLifecycle
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.event_router import EventRouter
from jarvis.core.state_manager import GlobalStateManager
from jarvis.core.resource_manager import ResourceManager
from jarvis.core.health_monitor import HealthMonitor
from jarvis.core.runtime_database import RuntimeDatabase
from jarvis.core.startup_manager import StartupManager
from jarvis.core.shutdown_manager import ShutdownManager
from jarvis.core.diagnostics import DiagnosticsEngine
from jarvis.core.telemetry import TelemetryTracker

logger = logging.getLogger("JARVIS.Core.Orchestrator")

class MasterOrchestrator:
    """Central entry facade coordinating lifecycle sequences, diagnostics, and routing between modules."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.lifecycle = RuntimeLifecycle.INITIALIZING
        self.registry = ServiceRegistry()
        self.event_router = EventRouter()
        self.state_manager = GlobalStateManager()
        self.resource_manager = ResourceManager()
        self.health_monitor = HealthMonitor(self.registry)
        self.db = RuntimeDatabase(db_path=db_path)
        self.diagnostics = DiagnosticsEngine()
        self.telemetry = TelemetryTracker()
        
        self.startup_mgr = StartupManager(self.registry, self.db)
        self.shutdown_mgr = ShutdownManager(self.registry, self.db)
        
        self.db.log_lifecycle_event("INITIALIZED", "MasterOrchestrator setup completed.")

    def cold_boot(self) -> bool:
        """Launches the StartupManager, setting lifecycle states to STARTING and RUNNING."""
        logger.info("MasterOrchestrator cold boot initiated...")
        self.lifecycle = RuntimeLifecycle.STARTING
        
        success = self.startup_mgr.execute_boot()
        if success:
            self.lifecycle = RuntimeLifecycle.RUNNING
            self.state_manager.update_state("active_task", "Ready")
            self.db.log_lifecycle_event("RUNNING", "JARVIS OS cold boot completed.")
        else:
            self.lifecycle = RuntimeLifecycle.FAILED
            self.db.log_lifecycle_event("FAILED", "Cold boot startup crashed.")
            
        return success

    def graceful_shutdown(self) -> bool:
        """Triggers the ShutdownManager, closing folders and database connections."""
        logger.info("MasterOrchestrator graceful shutdown initiated...")
        self.lifecycle = RuntimeLifecycle.STOPPING
        
        success = self.shutdown_mgr.execute_shutdown()
        if success:
            self.lifecycle = RuntimeLifecycle.SHUTDOWN
            self.db.log_lifecycle_event("SHUTDOWN", "JARVIS OS gracefully stopped.")
        else:
            self.lifecycle = RuntimeLifecycle.FAILED
            self.db.log_lifecycle_event("FAILED", "Graceful shutdown crashed.")
            
        return success
