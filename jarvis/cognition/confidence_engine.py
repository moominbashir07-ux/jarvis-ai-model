import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Cognition.Confidence")

class ConfidenceEngine:
    """Computes evidence-based confidence metrics based on historical statistics."""

    def __init__(self):
        pass

    def estimate_confidence(self, success_count: int, failure_count: int) -> float:
        """Determines statistical probabilities values (0.00 to 1.00)."""
        logger.info(f"Estimating confidence weight: successes={success_count}, failures={failure_count}")
        total = success_count + failure_count
        if total == 0:
            return 0.5
            
        conf = float(success_count) / float(total)
        logger.info(f"Calculated confidence score: {conf:.2f}")
        return round(conf, 2)
