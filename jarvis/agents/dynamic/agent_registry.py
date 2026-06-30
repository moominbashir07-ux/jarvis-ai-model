import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JARVIS.Agents.Registry")

class DynamicAgentRegistry:
    """Manages dynamic agent state registration, version tags, and capability directories in SQLite."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dynamic_agents (
                    name TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    capabilities TEXT NOT NULL,
                    enabled INTEGER NOT NULL,
                    success_rate REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize agent registry SQLite database: {e}")

    def register_agent(self, name: str, version: str, capabilities: List[str], enabled: bool = True) -> bool:
        """Registers a new specialized dynamic agent configuration or updates metadata."""
        try:
            caps_str = ",".join(capabilities)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dynamic_agents (name, version, capabilities, enabled, success_rate)
                VALUES (?, ?, ?, ?, 1.0)
                ON CONFLICT(name) DO UPDATE SET
                    version = excluded.version,
                    capabilities = excluded.capabilities,
                    enabled = excluded.enabled
            """, (name, version, caps_str, 1 if enabled else 0))
            conn.commit()
            conn.close()
            logger.info(f"Registering dynamic agent: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register dynamic agent: {e}")
            return False

    def disable_agent(self, name: str) -> bool:
        """Deactivates a registered dynamic agent."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE dynamic_agents SET enabled = 0 WHERE name = ?", (name,))
            conn.commit()
            conn.close()
            logger.info(f"Deactivated dynamic agent: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable dynamic agent: {e}")
            return False

    def get_enabled_agents(self) -> List[Dict[str, Any]]:
        """Retrieves list of active/enabled dynamic agents."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, version, capabilities, success_rate FROM dynamic_agents WHERE enabled = 1")
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for r in rows:
                results.append({
                    "name": r[0],
                    "version": r[1],
                    "capabilities": r[2].split(","),
                    "success_rate": r[3]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to fetch active dynamic agents list: {e}")
            return []
