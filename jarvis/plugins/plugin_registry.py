import sqlite3
import logging
from typing import Dict, Any, List, Optional
from jarvis.plugins.plugin_manifest import PluginManifest

logger = logging.getLogger("JARVIS.Plugins.Registry")

class PluginRegistry:
    """Manages SQLite database mappings tracking plugin statuses, dependencies, and ratings."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugin_registry (
                    plugin_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    permissions TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize plugin registry SQLite database: {e}")

    def register_plugin(self, manifest: PluginManifest, status: str = "installed") -> bool:
        """Saves plugin registration configurations or updates current active states."""
        try:
            perms_str = ",".join(manifest.permissions)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO plugin_registry (plugin_id, name, version, status, permissions)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(plugin_id) DO UPDATE SET
                    name = excluded.name,
                    version = excluded.version,
                    status = excluded.status,
                    permissions = excluded.permissions
            """, (manifest.id, manifest.name, manifest.version, status, perms_str))
            conn.commit()
            conn.close()
            logger.info(f"Plugin registered in database: [{manifest.id}]")
            return True
        except Exception as e:
            logger.error(f"Failed to save plugin registry details: {e}")
            return False

    def update_plugin_status(self, plugin_id: str, status: str) -> bool:
        """Modifies plugin activation states (e.g. enabling, disabling)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE plugin_registry SET status = ? WHERE plugin_id = ?", (status, plugin_id))
            conn.commit()
            conn.close()
            logger.info(f"Updated status for [{plugin_id}] to '{status}'")
            return True
        except Exception as e:
            logger.error(f"Failed to update plugin status: {e}")
            return False

    def get_plugin_status(self, plugin_id: str) -> Optional[str]:
        """Loads registration status details for the plugin from database logs."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM plugin_registry WHERE plugin_id = ?", (plugin_id,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Failed to retrieve plugin status from registry: {e}")
            return None
