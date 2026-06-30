import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JARVIS.Plugins.Marketplace")

class PluginMarketplace:
    """Mock registry catalog simulating download directories for external plugins."""

    def __init__(self):
        self.catalog = {
            "weather_plugin": {
                "name": "Weather Plugin",
                "id": "weather_plugin",
                "version": "1.0.0",
                "category": "Utilities",
                "rating": 4.8,
                "compatibility": "JARVIS >= 1.0"
            },
            "git_helper": {
                "name": "Git Helper Plugin",
                "id": "git_helper",
                "version": "1.1.0",
                "category": "Development",
                "rating": 4.9,
                "compatibility": "JARVIS >= 1.0"
            }
        }

    def search_marketplace(self, query: str) -> List[Dict[str, Any]]:
        """Returns matching listings based on search key queries."""
        logger.info(f"Marketplace lookup: '{query}'")
        res = []
        for k, v in self.catalog.items():
            if query.lower() in v["name"].lower() or query.lower() in v["category"].lower():
                res.append(v)
        return res

    def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        return self.catalog.get(plugin_id)
