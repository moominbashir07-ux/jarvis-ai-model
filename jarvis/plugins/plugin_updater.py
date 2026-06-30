import os
import shutil
import logging
from typing import Dict, Any
from jarvis.plugins.plugin_manifest import PluginManifest
from jarvis.plugins.plugin_installer import PluginInstaller

logger = logging.getLogger("JARVIS.Plugins.Updater")

class PluginUpdater:
    """Checks package version increases, triggers updates, and handles rollbacks on errors."""

    def __init__(self, installer: PluginInstaller, backup_dir: str):
        self.installer = installer
        self.backup_dir = backup_dir

    def update_plugin(self, plugin_id: str, new_source_folder: str) -> Dict[str, Any]:
        """Upgrades a plugin, backing up active files to enable safety rollbacks."""
        logger.info(f"Initiating update process for plugin: '{plugin_id}'")
        
        active_dest = os.path.join(self.installer.target_dir, plugin_id)
        backup_path = os.path.join(self.backup_dir, f"{plugin_id}_backup")
        
        has_backup = False
        if os.path.exists(active_dest):
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(active_dest, backup_path)
            has_backup = True

        res = self.installer.install_plugin(new_source_folder)
        if not res["success"]:
            logger.error(f"Update failed: {res['error']}. Triggering rollback safety flow...")
            
            if has_backup:
                if os.path.exists(active_dest):
                    shutil.rmtree(active_dest)
                shutil.copytree(backup_path, active_dest)
                logger.info("Rollback safety sequence successfully finished.")
                
            return {"success": False, "error": f"Update failed: {res['error']}. Rollback triggered."}

        if has_backup and os.path.exists(backup_path):
            shutil.rmtree(backup_path)
            
        logger.info(f"Update verification check completed. Plugin '{plugin_id}' updated successfully.")
        return {"success": True, "manifest": res["manifest"]}
