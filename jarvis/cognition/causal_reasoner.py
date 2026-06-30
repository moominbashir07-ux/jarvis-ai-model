import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Cognition.Causal")

class CausalReasoner:
    """Builds cause-and-effect dependency graphs mapping causal chain sequences."""

    def __init__(self):
        self.causal_chain: List[str] = []

    def log_cause_and_effect(self, cause: str, effect: str):
        self.causal_chain.append(f"'{cause}' caused '{effect}'")
        logger.info(f"Causal event logged: '{cause}' => '{effect}'")
