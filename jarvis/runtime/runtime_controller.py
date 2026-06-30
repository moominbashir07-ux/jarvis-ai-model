import logging
from typing import Dict, Any
from jarvis.runtime.runtime import UnifiedRuntime
from jarvis.core.lifecycle import RuntimeLifecycle

logger = logging.getLogger("JARVIS.Runtime.Controller")

class RuntimeController:
    """Invokes system restarts, emergency recovery loops, and cleanups."""

    def __init__(self, runtime: UnifiedRuntime):
        self.runtime = runtime

    def warm_restart(self) -> bool:
        logger.info("Executing warm restart loop...")
        self.runtime.graceful_shutdown()
        
        self.runtime.lifecycle = RuntimeLifecycle.INITIALIZING
        self.runtime.db.log_lifecycle_event("RUNTIME_WARM_RESTART", "Re-booting master controller.")
        
        return self.runtime.cold_boot()

    def emergency_recovery(self) -> bool:
        logger.warning("Emergency recovery triggered! Attempting system restore...")
        self.runtime.lifecycle = RuntimeLifecycle.RECOVERING
        self.runtime.db.log_lifecycle_event("RUNTIME_EMERGENCY_RECOVERY", "Recovery sequence deployed.")
        
        return self.runtime.cold_boot()
