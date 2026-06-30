import os
import json
import shutil
import logging
from typing import Dict, Any, List, Optional
from jarvis.plugins.plugin_manifest import PluginManifest
from jarvis.plugins.permission_manager import PermissionManager
from jarvis.plugins.sandbox import PluginSandbox
from jarvis.plugins.plugin_api import PluginAPI
from jarvis.plugins.plugin_loader import PluginLoader
from jarvis.plugins.plugin_registry import PluginRegistry
from jarvis.plugins.plugin_validator import PluginValidator
from jarvis.plugins.plugin_installer import PluginInstaller
from jarvis.plugins.plugin_updater import PluginUpdater
from jarvis.plugins.plugin_context import PluginContext

logger = logging.getLogger("JARVIS.Plugins.Manager")

class PluginManager:
    """Core controller coordinating loaders, sandboxes, event notifications, and registries."""

    def __init__(self, workspace_dir: str, db_path: str = "jarvis_memory.db"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
        
        self.permissions = PermissionManager()
        self.registry = PluginRegistry(db_path=db_path)
        self.validator = PluginValidator()
        self.installer = PluginInstaller(workspace_dir, self.registry, self.validator)
        self.updater = PluginUpdater(self.installer, workspace_dir)
        
        def sandbox_factory(p_id: str):
            return PluginSandbox(p_id, self.permissions)
            
        self.loader = PluginLoader(sandbox_factory)
        
        self.active_plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_contexts: Dict[str, PluginContext] = {}

    def install_plugin_package(self, source_folder: str) -> Dict[str, Any]:
        return self.installer.install_plugin(source_folder)

    def load_and_enable_plugin(self, plugin_id: str) -> bool:
        """Hot-loads a plugin script inside its sandbox and triggers on_start lifecycle hooks."""
        logger.info(f"Enabling plugin: '{plugin_id}'")
        
        folder_path = os.path.join(self.workspace_dir, plugin_id)
        manifest_file = os.path.join(folder_path, "manifest.json")
        if not os.path.exists(manifest_file):
            logger.error(f"Cannot load plugin [{plugin_id}]: manifest file missing.")
            return False

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            manifest = PluginManifest(manifest_data)
            
            self.permissions.grant_permissions(manifest.id, manifest.permissions)
            
            api = PluginAPI(manifest.id, self.permissions)
            context = PluginContext(manifest.id)
            self.plugin_contexts[manifest.id] = context
            
            load_res = self.loader.load_plugin(folder_path, manifest, api)
            if not load_res["success"]:
                logger.error(f"Sandbox loading failed for [{manifest.id}]: {load_res['error']}")
                return False

            self.active_plugins[manifest.id] = {
                "manifest": manifest,
                "globals": load_res["globals"],
                "on_start": load_res["on_start"],
                "on_stop": load_res["on_stop"]
            }

            on_start = load_res["on_start"]
            if on_start and callable(on_start):
                logger.info(f"Invoking on_start lifecycle hook for: '{manifest.id}'")
                on_start()

            self.registry.update_plugin_status(manifest.id, "enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to enable plugin [{plugin_id}]: {e}")
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Triggers on_stop callbacks and unloads code scopes."""
        logger.info(f"Disabling plugin: '{plugin_id}'")
        
        if plugin_id in self.active_plugins:
            ref = self.active_plugins[plugin_id]
            on_stop = ref.get("on_stop")
            if on_stop and callable(on_stop):
                logger.info(f"Invoking on_stop hook for: '{plugin_id}'")
                try:
                    on_stop()
                except Exception as e:
                    logger.error(f"on_stop execution error: {e}")
            del self.active_plugins[plugin_id]

        if plugin_id in self.plugin_contexts:
            del self.plugin_contexts[plugin_id]

        self.registry.update_plugin_status(plugin_id, "disabled")
        return True

    def reload_plugin(self, plugin_id: str) -> bool:
        """Hot-unloads and re-loads plugin script configurations."""
        logger.info(f"Reloading plugin: '{plugin_id}'")
        self.disable_plugin(plugin_id)
        return self.load_and_enable_plugin(plugin_id)

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Shuts down and purges a plugin folder directory from disk."""
        logger.info(f"Uninstalling plugin: '{plugin_id}'")
        self.disable_plugin(plugin_id)
        
        dest_dir = os.path.join(self.workspace_dir, plugin_id)
        if os.path.exists(dest_dir):
            try:
                shutil.rmtree(dest_dir)
            except Exception as e:
                logger.error(f"Failed to purge folder directory: {e}")
                
        self.registry.update_plugin_status(plugin_id, "uninstalled")
        return True
