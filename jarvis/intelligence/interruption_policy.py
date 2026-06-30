import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Intelligence.Policy")

class InterruptionPolicy:
    """Enforces non-intrusive suggestion policies based on workspace and CPU loads."""

    def __init__(self, mode: str = "Balanced"):
        self.mode = mode.upper()

    def set_mode(self, mode: str):
        self.mode = mode.upper()
        logger.info(f"Interruption policy mode updated: [{self.mode}]")

    def should_suppress(self, details: Dict[str, Any]) -> bool:
        """Evaluates details to verify interruption safety."""
        if self.mode == "SILENT":
            logger.debug("Suppressing suggestion: Interruption Mode is SILENT.")
            return True

        is_fullscreen = details.get("is_fullscreen", False)
        in_meeting = details.get("in_meeting", False)
        cpu_load = details.get("cpu_load", 0.0)

        if is_fullscreen:
            logger.info("Suppressing suggestion: User is running a full-screen application.")
            return True

        if in_meeting:
            logger.info("Suppressing suggestion: User is actively in a presentation or meeting.")
            return True

        if self.mode in ("BALANCED", "MINIMAL") and cpu_load > 80.0:
            logger.warning(f"Suppressing suggestion: System CPU load ({cpu_load:.1f}%) is high.")
            return True

        if self.mode == "MINIMAL":
            importance = details.get("importance", "NORMAL").upper()
            if importance != "HIGH":
                logger.debug("Suppressing suggestion: Minimal interruption mode blocks normal importance alerts.")
                return True

        return False
