import logging
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Intelligence.Workflow")

class WorkflowDetector:
    """Isolates repeating sequences of application switches and file updates."""

    def __init__(self, sequence_length: int = 3, match_threshold: int = 2):
        self.sequence_length = sequence_length
        self.match_threshold = match_threshold
        self.workflows: List[Dict[str, Any]] = []

    def analyze_sequence(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scans behavior log histories to group matching chronological steps."""
        app_switches = [
            log["details"]["app_name"] 
            for log in logs 
            if log["type"] == "APP_SWITCH" and log["details"].get("app_name")
        ]

        if len(app_switches) < self.sequence_length:
            return []

        sequences = []
        for i in range(len(app_switches) - self.sequence_length + 1):
            seq = tuple(app_switches[i : i + self.sequence_length])
            sequences.append(seq)

        freqs = {}
        for seq in sequences:
            freqs[seq] = freqs.get(seq, 0) + 1

        detected = []
        for seq, count in freqs.items():
            if count >= self.match_threshold:
                detected.append({
                    "sequence": list(seq),
                    "frequency": count,
                    "confidence": min(1.0, count * 0.25),
                    "name": f"Workspace Setup: {' -> '.join(seq)}"
                })
                
        self.workflows = detected
        return detected
