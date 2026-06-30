import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Cognition.Database")

class CognitiveDatabase:
    """Manages SQLite schemas persisting decision trees, reflection loops, and goals status logs."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cognition_goals (
                    goal_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    target_date TEXT,
                    confidence REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cognition_reflection_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id TEXT NOT NULL,
                    reflection TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize SQLite cognition database tables: {e}")

    def log_goal(self, goal_id: str, desc: str, status: str, target: str = "", conf: float = 1.0):
        """Pushes or updates a planning goal row."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cognition_goals (goal_id, description, status, target_date, confidence)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(goal_id) DO UPDATE SET
                    status = excluded.status,
                    confidence = excluded.confidence
            """, (goal_id, desc, status, target, conf))
            conn.commit()
            conn.close()
            logger.info(f"Cognitive goal logged: [{goal_id}] '{desc}' => '{status}'")
        except Exception as e:
            logger.error(f"Failed to log cognitive goal: {e}")

    def log_reflection(self, goal_id: str, reflection: str, success: bool):
        """Records self-reflection results to SQLite database logs."""
        try:
            import time
            t = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cognition_reflection_logs (goal_id, reflection, success, timestamp) VALUES (?, ?, ?, ?)",
                (goal_id, reflection, 1 if success else 0, t)
            )
            conn.commit()
            conn.close()
            logger.info(f"Reflection logged for goal: [{goal_id}] (success={success})")
        except Exception as e:
            logger.error(f"Failed to log reflection entry: {e}")
