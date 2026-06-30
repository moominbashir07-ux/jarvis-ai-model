import json
import logging
from typing import List, Dict, Any
from jarvis.personalization.db_helper import PersonalizationDB
from jarvis.personalization.preference_engine import PreferenceEngine

logger = logging.getLogger("JARVIS.Personalization.Recommendations")

class RecommendationEngine:
    """Computes context-aware file, app, or workspace recommendations weighted by user preferences."""

    def __init__(self, db: PersonalizationDB, preference_engine: PreferenceEngine):
        self.db = db
        self.prefs = preference_engine

    def generate_recommendations(self, current_app: str, recent_files: List[str]) -> List[Dict[str, Any]]:
        """Formulates recommendations dynamically weighted by preference multipliers."""
        recommendations = []

        workspace_mult = self.prefs.get_multiplier("workspace_prepare")
        if current_app == "Code.exe":
            base = 0.8
            score = base * workspace_mult
            recommendations.append({
                "id": "rec_workspace_restore",
                "category": "workspace_prepare",
                "title": "Prepare Coding Workspace",
                "confidence": min(1.0, score),
                "payload": {"action": "restore_layout", "ide": "VS Code"}
            })

        file_mult = self.prefs.get_multiplier("research_summary")
        for f in recent_files:
            if f.endswith((".pdf", ".txt", ".md")):
                score = 0.7 * file_mult
                recommendations.append({
                    "id": f"rec_summarize_{hash(f)}",
                    "category": "research_summary",
                    "title": f"Summarize {f}",
                    "confidence": min(1.0, score),
                    "payload": {"action": "summarize", "file": f}
                })

        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        try:
            for rec in recommendations:
                payload_str = json.dumps(rec["payload"])
                self.db.execute("""
                    INSERT INTO recommendations (id, category, title, confidence, payload_json)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        confidence = excluded.confidence,
                        payload_json = excluded.payload_json
                """, (rec["id"], rec["category"], rec["title"], rec["confidence"], payload_str))
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to save recommendations: {e}")

        return recommendations
