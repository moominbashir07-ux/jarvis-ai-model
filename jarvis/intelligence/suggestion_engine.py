import re
import logging
from typing import List, Dict, Any
from jarvis.intelligence.confidence_model import ConfidenceModel

logger = logging.getLogger("JARVIS.Intelligence.Suggestion")

class SuggestionEngine:
    """Matches workflow sequences and context snippets to formulate assistance recommendations."""

    def __init__(self, confidence_model: ConfidenceModel = None):
        self.confidence = confidence_model or ConfidenceModel()

    def generate_suggestions(
        self, 
        detected_workflows: List[Dict[str, Any]], 
        logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Maps behavioral patterns to structured, confidence-calibrated suggestions."""
        suggestions = []

        for flow in detected_workflows:
            seq = flow["sequence"]
            base_score = flow["confidence"]
            calibrated = self.confidence.calculate_score("workspace_prepare", base_score)

            if calibrated >= self.confidence.threshold:
                suggestions.append({
                    "id": f"sug_workspace_{'_'.join(seq)}",
                    "category": "workspace_prepare",
                    "title": f"Launch Workspace: {' -> '.join(seq)}",
                    "description": f"I noticed you repeatedly switch between {', '.join(seq)}. Would you like me to prepare this workspace automatically?",
                    "confidence_score": calibrated,
                    "action_payload": {"action": "open_apps", "apps": seq}
                })

        latest_clipboard = next((log for log in reversed(logs) if log["type"] == "CLIPBOARD_COPY"), None)
        if latest_clipboard:
            text = latest_clipboard["details"].get("text", "")
            email_match = re.search(r"[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]{2,}", text)
            if email_match:
                email = email_match.group(0)
                calibrated = self.confidence.calculate_score("outlook_compose", 0.75)
                if calibrated >= self.confidence.threshold:
                    suggestions.append({
                        "id": f"sug_outlook_{email}",
                        "category": "outlook_compose",
                        "title": f"Compose mail to {email}",
                        "description": f"You copied the email address '{email}'. Shall I open Outlook and compose a draft?",
                        "confidence_score": calibrated,
                        "action_payload": {"action": "open_email", "recipient": email}
                    })

        latest_file = next((log for log in reversed(logs) if log["type"] == "FILE_INTERACTION"), None)
        if latest_file:
            path = latest_file["details"].get("filepath", "")
            action = latest_file["details"].get("action", "")
            if path.endswith((".pdf", ".txt", ".md")) and action == "READ":
                calibrated = self.confidence.calculate_score("research_summary", 0.65)
                if calibrated >= self.confidence.threshold:
                    suggestions.append({
                        "id": f"sug_summarize_{hash(path)}",
                        "category": "research_summary",
                        "title": f"Summarize {path}",
                        "description": f"You're reading '{path}'. Would you like me to compile a brief research summary?",
                        "confidence_score": calibrated,
                        "action_payload": {"action": "summarize_file", "path": path}
                    })

        suggestions.sort(key=lambda s: s["confidence_score"], reverse=True)
        return suggestions
