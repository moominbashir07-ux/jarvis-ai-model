import time
import logging
from typing import Dict, Any, List
from jarvis.personalization.db_helper import PersonalizationDB

logger = logging.getLogger("JARVIS.Personalization.Predictions")

class GoalPredictionEngine:
    """Predicts upcoming user goals and registers probability scores inside SQLite."""

    def __init__(self, db: PersonalizationDB):
        self.db = db

    def predict_goals(self, app_history: List[str]) -> List[Dict[str, Any]]:
        """Maps recent application switches to likelihood probability scores of next steps."""
        predictions = []

        if not app_history:
            return []

        last_app = app_history[-1]
        
        if last_app == "Code.exe":
            predictions.append({"action": "Launch Terminal", "probability": 0.85})
            predictions.append({"action": "Open Chrome for Documentation", "probability": 0.65})
        elif last_app == "Chrome.exe":
            predictions.append({"action": "Resume Coding Session", "probability": 0.70})
            predictions.append({"action": "Write Documentation", "probability": 0.50})
        else:
            predictions.append({"action": "Open VS Code", "probability": 0.60})

        try:
            t = time.time()
            for pred in predictions:
                self.db.execute("""
                    INSERT INTO predictions (action, probability, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(action) DO UPDATE SET
                        probability = excluded.probability,
                        updated_at = excluded.updated_at
                """, (pred["action"], pred["probability"], t))
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to record goal predictions to SQLite: {e}")

        return predictions
