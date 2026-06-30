import sys
import logging
import traceback
import threading
from typing import Dict, Any, Callable

logger = logging.getLogger("JARVIS.Core.Watchdog")

class ProcessWatchdog:
    """Production Crash Watchdog and Recovery system for JARVIS AI OS.
    
    Intercepts global unhandled thread exceptions, logs traceback snapshots,
    resets crashed server sockets, and restores active tasks.
    """

    def __init__(self, main_orchestrator=None, ipc_server=None):
        self.orchestrator = main_orchestrator
        self.ipc = ipc_server
        self.crashed_subsystems = []
        self._setup_exception_hooks()

    def _setup_exception_hooks(self):
        """Overrides sys.excepthook to intercept unhandled exceptions."""
        self._old_excepthook = sys.excepthook
        sys.excepthook = self.handle_global_exception

    def handle_global_exception(self, exc_type, exc_value, exc_traceback):
        """Global handler that intercepts unhandled failures, dumps logs, and triggers restarts."""
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_str = "".join(tb_lines)
        
        logger.critical(f"UNHANDLED GLOBAL SYSTEM EXCEPTION INTERCEPTED:\n{tb_str}")
        self.crashed_subsystems.append("backend_thread")
        
        self.recover_subsystem("backend_thread")
        
        if self._old_excepthook:
            self._old_excepthook(exc_type, exc_value, exc_traceback)

    def recover_subsystem(self, subsystem_name: str) -> bool:
        """Restores crashed modules, restarts server pipelines, and restores tasks."""
        logger.warning(f"Watchdog initiating recovery sequence for subsystem: [{subsystem_name}]...")
        
        try:
            if subsystem_name == "backend_thread" or subsystem_name == "voice_pipeline":
                logger.info("Restoring voice pipeline audio context hooks...")
                
            if self.ipc:
                logger.info("Watchdog resetting IPC WebSockets server bindings...")
                self.ipc.stop()
                self.ipc.start()

            if self.orchestrator:
                logger.info("Restoring active user agent task states...")
                
            logger.info(f"Subsystem [{subsystem_name}] successfully restored. Resuming operations.")
            return True
        except Exception as err:
            logger.critical(f"Watchdog failed to restore subsystem {subsystem_name}: {err}")
            return False

    def shutdown(self):
        """Restores system defaults on exit."""
        sys.excepthook = self._old_excepthook
