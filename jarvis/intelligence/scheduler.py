import time
import logging
import threading
from typing import Dict, Any, Callable

logger = logging.getLogger("JARVIS.Intelligence.Scheduler")

class BackgroundScheduler:
    """Runs periodic proactive intelligence audits in the background."""

    def __init__(self, check_callback: Callable[[], None], interval_seconds: float = 10.0):
        self.check_callback = check_callback
        self.interval = interval_seconds
        self.is_running = False
        self.thread = None

    def start(self):
        """Launches the background polling thread loop."""
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="JARVIS-Proactive-Scheduler"
        )
        self.thread.start()
        logger.info(f"Background proactive scheduler active (Interval: {self.interval}s).")

    def _run_loop(self):
        while self.is_running:
            try:
                self.check_callback()
            except Exception as e:
                logger.error(f"Error executing proactive scheduler callback: {e}")
            time.sleep(self.interval)

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.debug("Background proactive scheduler stopped.")
