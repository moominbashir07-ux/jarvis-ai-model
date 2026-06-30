import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Intelligence.Tracker")

class BehaviorTracker:
    """Tracks active app logs, clipboard contents, and file histories with privacy filtering."""

    def __init__(self, history_limit: int = 100):
        self.history_limit = history_limit
        self.logs: List[Dict[str, Any]] = []
        
        self.redact_patterns = [
            re.compile(r"(?:api_key|password|secret|token|passwd|private_key)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{12,})['\"]?", re.IGNORECASE),
            re.compile(r"sk-[a-zA-Z0-9]{48}", re.IGNORECASE),
            re.compile(r"AIzaSy[a-zA-Z0-9_\-]{33}", re.IGNORECASE)
        ]

    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Logs behavior transitions. Redacts credentials automatically before storing."""
        redacted_details = self.redact_sensitive_fields(details)
        event = {
            "type": event_type.upper(),
            "details": redacted_details,
            "timestamp": details.get("timestamp") or float(details.get("timestamp", 0))
        }
        self.logs.append(event)
        if len(self.logs) > self.history_limit:
            self.logs.pop(0)

    def redact_sensitive_fields(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Iterates over dictionary elements to find and replace sensitive data patterns."""
        redacted = {}
        for key, val in details.items():
            if isinstance(val, str):
                redacted[key] = self.redact_string(val)
            elif isinstance(val, dict):
                redacted[key] = self.redact_sensitive_fields(val)
            else:
                redacted[key] = val
        return redacted

    def redact_string(self, text: str) -> str:
        """Applies regex search patterns to mask credential tokens."""
        for pattern in self.redact_patterns:
            matches = pattern.findall(text)
            for m in matches:
                text = text.replace(m, "[REDACTED_SENSITIVE_KEY]")
            if pattern.search(text) and not matches:
                text = "[REDACTED_SENSITIVE_KEY]"
        return text

    def get_logs(self) -> List[Dict[str, Any]]:
        return list(self.logs)

    def clear(self):
        self.logs.clear()
