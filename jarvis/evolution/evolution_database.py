import json
import time
import sqlite3
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JARVIS.Evolution.Database")

class EvolutionDatabase:
    """Manages SQLite database mappings tracking analysis runs, accepted proposals, and rollbacks."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evolution_history (
                    patch_id TEXT PRIMARY KEY,
                    target_file TEXT NOT NULL,
                    status TEXT NOT NULL,
                    benchmark_json TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize evolution SQLite database tables: {e}")

    def log_patch_status(self, patch_id: str, file_path: str, status: str, benchmark: Optional[Dict[str, Any]] = None):
        """Logs a patch lifecycle update event to SQLite database logs."""
        try:
            bench_str = json.dumps(benchmark) if benchmark else None
            t = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evolution_history (patch_id, target_file, status, benchmark_json, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(patch_id) DO UPDATE SET
                    status = excluded.status,
                    benchmark_json = excluded.benchmark_json,
                    timestamp = excluded.timestamp
            """, (patch_id, file_path, status, bench_str, t))
            conn.commit()
            conn.close()
            logger.info("CollectiveMemory updated successfully.")
        except Exception as e:
            logger.error(f"Failed to log evolution status: {e}")

    def get_patch_record(self, patch_id: str) -> Optional[Dict[str, Any]]:
        """Loads a patch record from SQLite database logs."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT target_file, status, benchmark_json FROM evolution_history WHERE patch_id = ?", (patch_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            return {
                "patch_id": patch_id,
                "target_file": row[0],
                "status": row[1],
                "benchmark": json.loads(row[2]) if row[2] else None
            }
        except Exception as e:
            logger.error(f"Failed to load patch record from evolution history: {e}")
            return None
