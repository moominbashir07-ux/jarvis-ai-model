import json
import time
import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Agents.Memory")

class CollectiveMemory:
    """Stores multi-agent dialogue traces, subtask histories, and performance metrics in SQLite."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collective_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    agent_sender TEXT NOT NULL,
                    message_json TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize collective memory database: {e}")

    def post_message(self, topic: str, sender: str, message: Dict[str, Any]):
        """Logs dialogue exchanges between dynamic agents to SQLite."""
        try:
            msg_str = json.dumps(message)
            t = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO collective_memory (topic, agent_sender, message_json, timestamp) VALUES (?, ?, ?, ?)",
                (topic, sender, msg_str, t)
            )
            conn.commit()
            conn.close()
            logger.info("CollectiveMemory updated successfully.")
        except Exception as e:
            logger.error(f"Failed to log message to collective memory: {e}")

    def get_messages(self, topic: str) -> List[Dict[str, Any]]:
        """Retrieves conversational trace history for a given topic."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT agent_sender, message_json, timestamp FROM collective_memory WHERE topic = ? ORDER BY id ASC",
                (topic,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for r in rows:
                results.append({
                    "sender": r[0],
                    "message": json.loads(r[1]),
                    "timestamp": r[2]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to load messages from collective memory: {e}")
            return []
