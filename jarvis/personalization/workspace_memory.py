import json
import time
import logging
from typing import Dict, Any, Optional
from jarvis.personalization.db_helper import PersonalizationDB

logger = logging.getLogger("JARVIS.Personalization.Workspace")

class WorkspaceMemory:
    """Saves active workspace files list and editor state configuration profiles to SQLite."""

    def __init__(self, db: PersonalizationDB):
        self.db = db

    def save_workspace_state(self, project_path: str, state_details: Dict[str, Any]):
        """Persists the state of a project directory workspace layout to SQLite."""
        try:
            state_str = json.dumps(state_details)
            t = time.time()
            self.db.execute("""
                INSERT INTO workspace_memory (key, state_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
            """, (project_path.strip().lower(), state_str, t))
            self.db.commit()
            logger.debug(f"Saved project workspace layout state for: '{project_path}'")
        except Exception as e:
            logger.error(f"Failed to record workspace layout details: {e}")

    def load_workspace_state(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Loads and parses the persisted layout state of a project directory workspace."""
        try:
            rows = self.db.execute(
                "SELECT state_json FROM workspace_memory WHERE key = ?",
                (project_path.strip().lower(),)
            )
            if not rows:
                return None
            return json.loads(rows[0]["state_json"])
        except Exception as e:
            logger.error(f"Failed to load workspace layout details: {e}")
            return None
