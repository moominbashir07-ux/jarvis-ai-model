import logging
from typing import Dict, Any, List
from jarvis.core.lifecycle import RuntimeLifecycle
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.event_router import EventRouter
from jarvis.core.state_manager import GlobalStateManager
from jarvis.core.resource_manager import ResourceManager
from jarvis.core.health_monitor import HealthMonitor
from jarvis.core.runtime_database import RuntimeDatabase
from jarvis.runtime.service_initializer import ServiceInitializer
from jarvis.runtime.module_connector import ModuleConnector
from jarvis.runtime.session_manager import SessionManager
from jarvis.runtime.request_router import RequestRouter
from jarvis.runtime.conversation_pipeline import ConversationPipeline
from jarvis.runtime.execution_pipeline import ExecutionPipeline
from jarvis.runtime.context_pipeline import ContextPipeline
from jarvis.runtime.shutdown_controller import ShutdownController
from jarvis.runtime.runtime_metrics import RuntimeMetrics
from jarvis.runtime.runtime_validator import RuntimeValidator

logger = logging.getLogger("JARVIS.Runtime.Core")

class UnifiedRuntime:
    """Consolidated master runtime coordinating lifecycle stages, event loops, and subsystems."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.lifecycle = RuntimeLifecycle.INITIALIZING
        self.registry = ServiceRegistry()
        self.event_router = EventRouter()
        self.state_manager = GlobalStateManager()
        self.resource_manager = ResourceManager()
        self.health_monitor = HealthMonitor(self.registry)
        self.db = RuntimeDatabase(db_path=db_path)
        
        self.initializer = ServiceInitializer(self.registry, self.db)
        self.connector = ModuleConnector(self.registry)
        self.session = SessionManager()
        self.router = RequestRouter()
        
        self.conversation = ConversationPipeline()
        self.execution = ExecutionPipeline()
        self.context = ContextPipeline()
        self.shutdown_ctrl = ShutdownController(self.registry, self.db)
        self.metrics = RuntimeMetrics()
        self.validator = RuntimeValidator(self.registry)
        
        self.db.log_lifecycle_event("RUNTIME_INITIALIZED", "UnifiedRuntime initialized successfully.")

    def cold_boot(self) -> bool:
        """Sequential cold-boot starting databases, loading plugins, and starting voice pipelines."""
        logger.info("UnifiedRuntime cold boot sequence initiated...")
        self.lifecycle = RuntimeLifecycle.STARTING
        
        init_ok = self.initializer.boot_all_services()
        if not init_ok:
            self.lifecycle = RuntimeLifecycle.FAILED
            self.db.log_lifecycle_event("RUNTIME_BOOT_FAILED", "Initialization crashed.")
            return False
            
        conn_ok = self.connector.verify_connections()
        if not conn_ok:
            self.lifecycle = RuntimeLifecycle.FAILED
            self.db.log_lifecycle_event("RUNTIME_CONN_FAILED", "Connectivity verification failed.")
            return False
            
        self.lifecycle = RuntimeLifecycle.RUNNING
        self.state_manager.update_state("active_task", "Ready")
        self.db.log_lifecycle_event("RUNTIME_RUNNING", "UnifiedRuntime boot completed successfully.")
        return True

    def graceful_shutdown(self) -> bool:
        """Sequentially deactivates services and releases database files."""
        logger.info("UnifiedRuntime graceful shutdown initiated...")
        self.lifecycle = RuntimeLifecycle.STOPPING
        
        success = self.shutdown_ctrl.execute_shutdown()
        if success:
            self.lifecycle = RuntimeLifecycle.SHUTDOWN
            self.db.log_lifecycle_event("RUNTIME_STOPPED", "UnifiedRuntime stopped.")
        else:
            self.lifecycle = RuntimeLifecycle.FAILED
            self.db.log_lifecycle_event("RUNTIME_STOP_FAILED", "Graceful shutdown crashed.")
            
        return success
