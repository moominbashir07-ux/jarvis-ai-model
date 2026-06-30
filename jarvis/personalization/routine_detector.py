import json
import time
import logging
from typing import List, Dict, Any
from jarvis.personalization.db_helper import PersonalizationDB

logger = logging.getLogger("JARVIS.Personalization.Routines")

class RoutineDetector:
    """Groups repeating actions sequences into high-level automated routines stored in SQLite."""

    def __init__(self, db: PersonalizationDB):
        self.db = db

    def register_routine(self, name: str, sequence: List[str], confidence: float):
        """Registers or updates a detected routine template in SQLite."""
        try:
            seq_str = json.dumps(sequence)
            t = time.time()
            self.db.execute("""
                INSERT INTO routines (name, sequence_json, confidence, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    sequence_json = excluded.sequence_json,
                    confidence = excluded.confidence,
                    created_at = excluded.created_at
            """, (name, seq_str, confidence, t))
            self.db.commit()
            logger.debug(f"Registered Routine profile: '{name}' (Confidence: {confidence:.2f})")
        except Exception as e:
            logger.error(f"Failed to save routine template: {e}")

    def get_detected_routines(self) -> List[Dict[str, Any]]:
        """Retrieves list of all detected routines stored in the database."""
        try:
            rows = self.db.execute("SELECT name, sequence_json, confidence FROM routines")
            results = []
            for row in rows:
                results.append({
                    "name": row["name"],
                    "sequence": json.loads(row["sequence_json"]),
                    "confidence": row["confidence"]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to load routines: {e}")
            return []
