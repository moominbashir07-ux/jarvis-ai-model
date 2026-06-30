import json
import time
import logging
from typing import Dict, Any, Optional
from jarvis.personalization.db_helper import PersonalizationDB

logger = logging.getLogger("JARVIS.Personalization.Profile")

class UserProfileManager:
    """Manages long-term user preferences (IDE, AI Provider, language) with JSON import/export and db rollback."""

    def __init__(self, db: PersonalizationDB):
        self.db = db

    def set_preference(self, key: str, value: Any):
        """Sets a key-value user preference field."""
        try:
            val_str = json.dumps(value)
            t = time.time()
            self.db.execute(
                "INSERT INTO user_profile (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, val_str, t)
            )
            self.db.commit()
            logger.debug(f"User preference saved: [{key}] -> {value}")
        except Exception as e:
            logger.error(f"Failed to set user preference: {e}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieves a key-value user preference field."""
        try:
            rows = self.db.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            if not rows:
                return default
            return json.loads(rows[0]["value"])
        except Exception as e:
            logger.error(f"Failed to fetch user preference: {e}")
            return default

    def export_profile(self) -> str:
        """Serializes the entire user profile to a JSON string."""
        try:
            rows = self.db.execute("SELECT key, value FROM user_profile")
            profile = {row["key"]: json.loads(row["value"]) for row in rows}
            return json.dumps(profile, indent=2)
        except Exception as e:
            logger.error(f"Failed to export user profile: {e}")
            return "{}"

    def import_profile(self, profile_json: str) -> bool:
        """Loads and overwrites user profile fields from a JSON string."""
        try:
            profile = json.loads(profile_json)
            t = time.time()
            for key, val in profile.items():
                self.set_preference(key, val)
            logger.info("Successfully imported user profile.")
            return True
        except Exception as e:
            logger.error(f"Failed to import user profile: {e}")
            return False
