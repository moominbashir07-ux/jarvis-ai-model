import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Intelligence.Confidence")

class ConfidenceModel:
    """Calculates recommendation scores dynamically using historical feedback logs."""

    def __init__(self, base_threshold: float = 0.5):
        self.threshold = base_threshold
        self.feedback_multipliers: Dict[str, float] = {
            "workspace_prepare": 1.0,
            "outlook_compose": 1.0,
            "research_summary": 1.0
        }

    def calculate_score(self, category: str, base_confidence: float) -> float:
        """Applies feedback modifiers to calculate calibrated confidence scores."""
        mult = self.feedback_multipliers.get(category, 1.0)
        final_score = base_confidence * mult
        logger.info(f"Calibrated confidence for [{category}]: {final_score:.2f} (Base: {base_confidence:.2f}, Mult: {mult:.2f})")
        return min(1.0, max(0.0, final_score))

    def record_feedback(self, category: str, action: str):
        """Adjusts category multipliers based on user interaction (accept, reject, ignore)."""
        current = self.feedback_multipliers.get(category, 1.0)
        
        if action == "ACCEPT":
            self.feedback_multipliers[category] = min(2.0, current + 0.15)
            logger.info(f"Feedback ACCEPT recorded. Increased multiplier for [{category}] to {self.feedback_multipliers[category]:.2f}")
        elif action == "REJECT":
            self.feedback_multipliers[category] = max(0.1, current - 0.25)
            logger.warning(f"Feedback REJECT recorded. Decreased multiplier for [{category}] to {self.feedback_multipliers[category]:.2f}")
        elif action == "IGNORE":
            self.feedback_multipliers[category] = max(0.2, current - 0.05)
            logger.info(f"Feedback IGNORE recorded. Decayed multiplier for [{category}] to {self.feedback_multipliers[category]:.2f}")
