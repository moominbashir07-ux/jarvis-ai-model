import time
import logging
from typing import Dict, Any, List
from jarvis.personalization.db_helper import PersonalizationDB

logger = logging.getLogger("JARVIS.Personalization.Habits")

class HabitLearningEngine:
    """Records application transitions, command frequencies, and active session habits to SQLite."""

    def __init__(self, db: PersonalizationDB):
        self.db = db

    def record_activity(self, activity_name: str):
        """Increments count frequency for user habit events."""
        try:
            t = time.time()
            self.db.execute("""
                INSERT INTO habits (habit_name, count, last_observed)
                VALUES (?, 1, ?)
                ON CONFLICT(habit_name) DO UPDATE SET
                    count = habits.count + 1,
                    last_observed = excluded.last_observed
            """, (activity_name.lower().strip(), t))
            self.db.commit()
            logger.debug(f"Habit registered: [{activity_name}]")
        except Exception as e:
            logger.error(f"Failed to record activity in habit database: {e}")

    def get_habit_frequency(self, activity_name: str) -> int:
        """Returns the frequency count of a specific activity habit."""
        try:
            rows = self.db.execute("SELECT count FROM habits WHERE habit_name = ?", (activity_name.lower().strip(),))
            if not rows:
                return 0
            return rows[0]["count"]
        except Exception as e:
            logger.error(f"Failed to fetch habit frequency: {e}")
            return 0

    def get_frequent_habits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves a list of top recorded habits ordered by frequency count."""
        try:
            rows = self.db.execute("SELECT habit_name, count, last_observed FROM habits ORDER BY count DESC LIMIT ?", (limit,))
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to load top habits: {e}")
            return []
