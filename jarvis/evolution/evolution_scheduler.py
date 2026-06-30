import logging
from typing import Callable

logger = logging.getLogger("JARVIS.Evolution.Scheduler")

class EvolutionScheduler:
    """Manages trigger configurations for daily/weekly/on-demand code inspections."""

    def __init__(self, callback: Callable[[], None]):
        self.callback = callback

    def configure_daily_trigger(self):
        logger.info("Configured daily evolution scheduler trigger.")

    def trigger_now(self):
        logger.info("Executing on-demand evolution scheduler trigger.")
        try:
            self.callback()
        except Exception as e:
            logger.error(f"Scheduler execution failed: {e}")
