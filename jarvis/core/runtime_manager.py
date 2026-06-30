import logging
from typing import Dict, Any
from jarvis.core.master_orchestrator import MasterOrchestrator
from jarvis.core.lifecycle import RuntimeLifecycle

logger = logging.getLogger("JARVIS.Core.Runtime")

class RuntimeManager:
    """Orchestrates system warm restarts, suspends, and emergency recoveries."""

    def __init__(self, orchestrator: MasterOrchestrator):
        self.orchestrator = orchestrator

    def warm_restart(self) -> bool:
        """Executes shutdown followed by initialization sequences."""
        logger.info("Initiating warm restart cycle...")
        self.orchestrator.graceful_shutdown()
        
        self.orchestrator.lifecycle = RuntimeLifecycle.INITIALIZING
        self.orchestrator.db.log_lifecycle_event("WARM_RESTART", "Initiated service reinstantiation.")
        
        return self.orchestrator.cold_boot()

    def emergency_recovery(self) -> bool:
        """Forces deactivation of failed services and spawns recoveries."""
        logger.warning("Emergency recovery triggered. Reinitializing system state...")
        self.orchestrator.lifecycle = RuntimeLifecycle.RECOVERING
        self.orchestrator.db.log_lifecycle_event("EMERGENCY_RECOVERY", "Recovery sequence deployed.")
        
        return self.orchestrator.cold_boot()
