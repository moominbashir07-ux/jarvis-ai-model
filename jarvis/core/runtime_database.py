import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Core.RuntimeDB")

class RuntimeDatabase:
    """Manages SQLite database schemas tracking boots durations, crash logs, and lifecycle transitions."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runtime_lifecycle_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT NOT NULL,
                    details TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize lifecycle SQLite database logs tables: {e}")

    def log_lifecycle_event(self, event: str, details: str = ""):
        """Records a startup/shutdown lifecycle step to SQLite database logs."""
        try:
            import time
            t = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO runtime_lifecycle_logs (event_name, details, timestamp) VALUES (?, ?, ?)",
                (event.strip(), details.strip(), t)
            )
            conn.commit()
            conn.close()
            logger.debug(f"Lifecycle event logged: '{event}'")
        except Exception as e:
            logger.error(f"Failed to log lifecycle event to database: {e}")
