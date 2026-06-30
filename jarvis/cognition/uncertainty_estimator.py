import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Cognition.Uncertainty")

class UncertaintyEstimator:
    """Flags uncertainty bounds (unknown vs highly certain) to avoid hallucinated parameters."""

    def __init__(self):
        pass

    def estimate_uncertainty(self, evidence_count: int, contradictions_count: int) -> str:
        """Determines certainty range bounds."""
        logger.info(f"Auditing evidence counts: evidence={evidence_count}, contradictions={contradictions_count}")
        
        if evidence_count > 5 and contradictions_count == 0:
            status = "highly_certain"
        elif evidence_count > 0:
            status = "partially_known"
        else:
            status = "unknown"
            
        logger.info(f"Uncertainty status: '{status}'")
        return status
