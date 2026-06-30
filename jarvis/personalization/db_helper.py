import os
import json
import sqlite3
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Personalization.DB")

class PersonalizationDB:
    """Manages SQLite schema initialization, indices, migrations, and backups for personalization data."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.init_schema()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL;")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite memory: {e}")

    def execute(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Executes a SQL query and returns rows."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def init_schema(self):
        """Creates the personalization database schemas with safe indexes."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    category TEXT PRIMARY KEY,
                    multiplier REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_name TEXT UNIQUE NOT NULL,
                    count INTEGER NOT NULL,
                    last_observed REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routines (
                    name TEXT PRIMARY KEY,
                    sequence_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    action TEXT PRIMARY KEY,
                    probability REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    payload_json TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workspace_memory (
                    key TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_habits_name ON habits (habit_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_sug ON feedback_history (suggestion_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_ts ON learning_events (timestamp);")
            
            self.conn.commit()
            logger.info("Personalization database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to verify or build personalization schema: {e}")

    def create_backup(self, backup_path: str = "logs/personalization_backup.bak") -> bool:
        """Saves a binary file backup copy of the database."""
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            backup_conn = sqlite3.connect(backup_path)
            with backup_conn:
                self.conn.backup(backup_conn)
            backup_conn.close()
            logger.info(f"Database backup created at: '{backup_path}'")
            return True
        except Exception as e:
            logger.error(f"Failed to back up database: {e}")
            return False

    def restore_backup(self, backup_path: str = "logs/personalization_backup.bak") -> bool:
        """Restores state from a backup database file."""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found at: '{backup_path}'")
                return False
            backup_conn = sqlite3.connect(backup_path)
            with self.conn:
                backup_conn.backup(self.conn)
            backup_conn.close()
            logger.info("Database successfully restored from backup.")
            return True
        except Exception as e:
            logger.error(f"Failed to restore database from backup: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            logger.debug("Personalization SQLite connection closed.")
