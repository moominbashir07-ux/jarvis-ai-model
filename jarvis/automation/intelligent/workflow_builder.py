import json
import time
import sqlite3
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JARVIS.Automation.Workflow")

class WorkflowBuilder:
    """Saves automation histories, durations, and successful sequences to SQLite."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS automation_memory (
                    workflow_name TEXT PRIMARY KEY,
                    steps_json TEXT NOT NULL,
                    success_rate REAL NOT NULL,
                    last_duration REAL NOT NULL,
                    last_run REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize automation database tables: {e}")

    def save_workflow(self, name: str, steps: List[Dict[str, Any]], success_rate: float, duration: float):
        """Records a successful sequence to SQLite database."""
        try:
            steps_str = json.dumps(steps)
            t = time.time()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO automation_memory (workflow_name, steps_json, success_rate, last_duration, last_run)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(workflow_name) DO UPDATE SET
                    steps_json = excluded.steps_json,
                    success_rate = excluded.success_rate,
                    last_duration = excluded.last_duration,
                    last_run = excluded.last_run
            """, (name.strip(), steps_str, success_rate, duration, t))
            conn.commit()
            conn.close()
            
            logger.info(f"Workflow stored: '{name}'")
        except Exception as e:
            logger.error(f"Failed to record workflow macro: {e}")

    def get_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """Loads a stored workflow sequence from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT steps_json, success_rate, last_duration FROM automation_memory WHERE workflow_name = ?", (name.strip(),))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            return {
                "name": name,
                "steps": json.loads(row[0]),
                "success_rate": row[1],
                "last_duration": row[2]
            }
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            return None
