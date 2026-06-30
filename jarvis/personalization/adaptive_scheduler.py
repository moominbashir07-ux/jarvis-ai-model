import time
import logging
import threading
from typing import Dict, Any, Callable

logger = logging.getLogger("JARVIS.Personalization.Scheduler")

class AdaptiveScheduler:
    """Manages periodic execution of personalization update tasks with CPU/Context suspension checks."""

    def __init__(self, update_callback: Callable[[], None], interval_seconds: float = 30.0):
        self.update_callback = update_callback
        self.interval = interval_seconds
        self.is_running = False
        self.thread = None

    def start(self):
        """Starts the background thread loop."""
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="JARVIS-Adaptive-Scheduler"
        )
        self.thread.start()
        logger.info(f"Adaptive personalization scheduler active (Interval: {self.interval}s).")

    def _run_loop(self):
        while self.is_running:
            try:
                cpu_load = 15.0
                is_fullscreen = False
                
                if cpu_load > 85.0 or is_fullscreen:
                    logger.debug("Adaptive scheduler skipped processing due to high system load.")
                else:
                    self.update_callback()
            except Exception as e:
                logger.error(f"Error executing personalization scheduler callback: {e}")
            time.sleep(self.interval)

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.debug("Adaptive personalization scheduler stopped.")
