import time
import logging
from typing import Dict, Any
from jarvis.personalization.db_helper import PersonalizationDB

logger = logging.getLogger("JARVIS.Personalization.Preferences")

class PreferenceEngine:
    """Manages adaptive scoring modifiers and feedback history tracking inside SQLite."""

    def __init__(self, db: PersonalizationDB):
        self.db = db

    def get_multiplier(self, category: str) -> float:
        """Loads preference multiplier rating for a specific action category."""
        try:
            rows = self.db.execute("SELECT multiplier FROM preferences WHERE category = ?", (category.lower().strip(),))
            if not rows:
                return 1.0
            return rows[0]["multiplier"]
        except Exception as e:
            logger.error(f"Failed to fetch preference multiplier: {e}")
            return 1.0

    def adjust_multiplier(self, category: str, delta: float):
        """Applies modifier delta value to dynamic ratings."""
        try:
            current = self.get_multiplier(category)
            new_val = min(2.0, max(0.1, current + delta))
            t = time.time()
            self.db.execute("""
                INSERT INTO preferences (category, multiplier, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(category) DO UPDATE SET
                    multiplier = excluded.multiplier,
                    updated_at = excluded.updated_at
            """, (category.lower().strip(), new_val, t))
            self.db.commit()
            logger.debug(f"Adjusted preference [{category}] from {current:.2f} to {new_val:.2f}")
        except Exception as e:
            logger.error(f"Failed to update preference multiplier: {e}")

    def log_feedback(self, suggestion_id: str, category: str, action: str):
        """Records suggestion acceptance/rejection to database and adapts ratings."""
        try:
            t = time.time()
            self.db.execute(
                "INSERT INTO feedback_history (suggestion_id, action, timestamp) VALUES (?, ?, ?)",
                (suggestion_id, action.upper(), t)
            )
            self.db.commit()
            
            delta = 0.0
            if action.upper() == "ACCEPT":
                delta = 0.15
            elif action.upper() == "REJECT":
                delta = -0.25
            elif action.upper() == "IGNORE":
                delta = -0.05
                
            self.adjust_multiplier(category, delta)
            logger.info(f"Feedback logged: [{action.upper()}] Suggestion: {suggestion_id} (Delta: {delta:+.2f})")
        except Exception as e:
            logger.error(f"Failed to record feedback logging: {e}")
