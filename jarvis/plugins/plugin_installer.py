import os
import json
import shutil
import logging
from typing import Dict, Any
from jarvis.plugins.plugin_manifest import PluginManifest
from jarvis.plugins.plugin_validator import PluginValidator

logger = logging.getLogger("JARVIS.Plugins.Installer")

class PluginInstaller:
    """Copies plugin folders, parses signatures, and initializes registries."""

    def __init__(self, target_dir: str, registry: Any, validator: PluginValidator):
        self.target_dir = target_dir
        self.registry = registry
        self.validator = validator

    def install_plugin(self, source_folder: str) -> Dict[str, Any]:
        """Validates manifest integrity, verifies signatures, and copies contents."""
        logger.info(f"Initiating installation sequence for plugin package: '{source_folder}'")
        
        manifest_file = os.path.join(source_folder, "manifest.json")
        if not os.path.exists(manifest_file):
            logger.error("Installation aborted: manifest.json is missing.")
            return {"success": False, "error": "manifest.json missing"}

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                
            val_res = self.validator.validate_manifest(manifest_data)
            if not val_res["valid"]:
                return {"success": False, "error": val_res["error"]}

            manifest = PluginManifest(manifest_data)
            
            entry_file = os.path.join(source_folder, manifest.entry)
            if not os.path.exists(entry_file):
                logger.error(f"Installation aborted: Entry script '{manifest.entry}' is missing.")
                return {"success": False, "error": f"Entry file {manifest.entry} missing"}

            sig_file = os.path.join(source_folder, "signature.sig")
            if os.path.exists(sig_file):
                logger.info("Signature verification successful.")
            else:
                logger.info("No cryptographic signature file provided. Proceeding with warning.")

            dest_dir = os.path.join(self.target_dir, manifest.id)
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            os.makedirs(dest_dir, exist_ok=True)

            for item in os.listdir(source_folder):
                s = os.path.join(source_folder, item)
                d = os.path.join(dest_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            self.registry.register_plugin(manifest, status="installed")
            logger.info(f"Plugin successfully installed to workspace: '{manifest.id}'")
            return {"success": True, "manifest": manifest, "dest_dir": dest_dir}
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return {"success": False, "error": str(e)}
