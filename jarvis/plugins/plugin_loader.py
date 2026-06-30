import os
import logging
from typing import Dict, Any, Optional
from jarvis.plugins.sandbox import PluginSandbox
from jarvis.plugins.plugin_manifest import PluginManifest
from jarvis.plugins.plugin_api import PluginAPI

logger = logging.getLogger("JARVIS.Plugins.Loader")

class PluginLoader:
    """Loads a plugin package, validates its structure, and compiles script entrypoints inside restricted sandboxes."""

    def __init__(self, sandbox_factory: Any):
        self.sandbox_factory = sandbox_factory

    def load_plugin(self, folder_path: str, manifest: PluginManifest, api_instance: PluginAPI) -> Dict[str, Any]:
        """Loads and compiles main script entrypoint."""
        entry_file = os.path.join(folder_path, manifest.entry)
        if not os.path.exists(entry_file):
            logger.error(f"Plugin entry file missing: '{entry_file}'")
            return {"success": False, "error": f"Entry file {manifest.entry} not found"}

        try:
            with open(entry_file, "r", encoding="utf-8") as f:
                code = f.read()
                
            sandbox = self.sandbox_factory(manifest.id)
            res = sandbox.execute_code(code, api_instance)
            return res
        except Exception as e:
            logger.error(f"Failed to load plugin: {e}")
            return {"success": False, "error": str(e)}
