import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Plugins.Manifest")

class PluginManifest:
    """Parses and exposes standard plugin manifest properties loaded from manifest.json."""

    def __init__(self, manifest_data: Dict[str, Any]):
        self.name = manifest_data.get("name", "Unknown Plugin")
        self.id = manifest_data.get("id", "unknown_plugin")
        self.version = manifest_data.get("version", "1.0.0")
        self.author = manifest_data.get("author", "Developer")
        self.description = manifest_data.get("description", "")
        self.permissions: List[str] = manifest_data.get("permissions", [])
        self.entry = manifest_data.get("entry", "main.py")
        self.api_version = manifest_data.get("api_version", "1.0")

    @classmethod
    def from_json(cls, json_str: str) -> "PluginManifest":
        """Builds a PluginManifest instance by parsing a JSON string."""
        data = json.loads(json_str)
        return cls(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "permissions": self.permissions,
            "entry": self.entry,
            "api_version": self.api_version
        }
