import os
import sys
import json
import shutil
import logging
from jarvis.core.logger import setup_logger
from jarvis.plugins.plugin_manifest import PluginManifest
from jarvis.plugins.permission_manager import PermissionManager
from jarvis.plugins.sandbox import PluginSandbox
from jarvis.plugins.plugin_api import PluginAPI
from jarvis.plugins.plugin_loader import PluginLoader
from jarvis.plugins.plugin_registry import PluginRegistry
from jarvis.plugins.plugin_validator import PluginValidator
from jarvis.plugins.plugin_installer import PluginInstaller
from jarvis.plugins.plugin_updater import PluginUpdater
from jarvis.plugins.plugin_marketplace import PluginMarketplace
from jarvis.plugins.plugin_manager import PluginManager

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestPluginSDK")

def test_plugin_sdk_pipeline():
    logger.info("==========================================")
    logger.info("      Plugin SDK (Phase G) Test           ")
    logger.info("==========================================")

    # Setup directories
    src_dir = "logs/test_source_plugin"
    updated_src_dir = "logs/test_updated_source_plugin"
    workspace_dir = "logs/test_plugins_workspace"
    db_path = "logs/test_plugin_memory.db"

    # Purge existing
    for path in (src_dir, updated_src_dir, workspace_dir):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                pass
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(updated_src_dir, exist_ok=True)

    # Create mockup manifest.json
    manifest_data = {
        "name": "Weather Plugin",
        "id": "weather_plugin",
        "version": "1.0.0",
        "author": "Developer",
        "description": "Provides weather updates",
        "permissions": ["notifications", "filesystem_read"],
        "entry": "main.py",
        "api_version": "1.0"
    }
    
    with open(os.path.join(src_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    # Create main.py entry script registering lifecycle callbacks
    plugin_code = """
started = False
stopped = False

def on_start():
    global started
    started = True
    jarvis_api.log_message("Weather Plugin started successfully.")
    jarvis_api.trigger_notification("Weather", "Temp is 72F")

def on_stop():
    global stopped
    stopped = True
    jarvis_api.log_message("Weather Plugin stopped.")
"""
    with open(os.path.join(src_dir, "main.py"), "w", encoding="utf-8") as f:
        f.write(plugin_code)

    # 1. Manifest Parsing & Validator Check
    logger.info("Testing manifest validation...")
    validator = PluginValidator()
    val_res = validator.validate_manifest(manifest_data)
    logger.info(f"Validator result: {val_res}")
    if not val_res["valid"]:
        logger.error("Manifest validation failed on valid manifest!")
        return False
        
    # Test invalid version validation fail
    invalid_manifest = manifest_data.copy()
    invalid_manifest["version"] = "1.0" # Should be major.minor.patch
    val_fail = validator.validate_manifest(invalid_manifest)
    if val_fail["valid"]:
        logger.error("Validator failed to reject non-semantic version format!")
        return False
    logger.info("Manifest Validator: [PASS]")

    # 2. Permission Verification Manager
    logger.info("Testing permission scopes manager...")
    perm_mgr = PermissionManager()
    perm_mgr.grant_permissions("weather_plugin", ["notifications", "filesystem_read"])
    if not perm_mgr.verify_permission("weather_plugin", "notifications"):
        logger.error("Permission Manager failed to identify granted scope!")
        return False
    if perm_mgr.verify_permission("weather_plugin", "internet"):
        logger.error("Permission Manager granted unauthorized scope!")
        return False
    logger.info("Permission Scopes Manager: [PASS]")

    # 3. Sandbox Restrictions & Security Checking
    logger.info("Testing import sandboxing and exec/eval blocks...")
    sandbox = PluginSandbox("weather_plugin", perm_mgr)
    api = PluginAPI("weather_plugin", perm_mgr)
    
    # Try importing disallowed package (sys)
    unsafe_code = """
import sys
"""
    sandbox_res = sandbox.execute_code(unsafe_code, api)
    logger.info(f"Sandbox unsafe import result success: {sandbox_res['success']} | Error: {sandbox_res['error']}")
    if sandbox_res["success"] or "blocked" not in sandbox_res["error"]:
        logger.error("Sandbox failed to block dangerous package import!")
        return False
        
    # Test file reading permissions (should succeed because filesystem_read was granted)
    with open("logs/test_file.txt", "w", encoding="utf-8") as f:
        f.write("Secured data payload")
    
    file_code = """
import os
content = jarvis_api.read_local_file("logs/test_file.txt")
jarvis_api.log_message(f"Read file payload: {content}")
"""
    file_res = sandbox.execute_code(file_code, api)
    logger.info(f"File sandbox check success: {file_res['success']}")
    if not file_res["success"]:
        logger.error(f"Sandbox failed to allow authorized files read: {file_res['error']}")
        return False
        
    # Clean file
    if os.path.exists("logs/test_file.txt"):
        os.remove("logs/test_file.txt")
    logger.info("Sandbox Isolation: [PASS]")

    # 4. Manager Lifecycles & Hot loading
    logger.info("Testing manager hot-loading installation and lifecycles...")
    manager = PluginManager(workspace_dir=workspace_dir, db_path=db_path)
    
    inst_res = manager.install_plugin_package(src_dir)
    logger.info(f"Installation result success: {inst_res['success']}")
    if not inst_res["success"]:
        logger.error("PluginManager failed to install valid package!")
        return False

    load_res = manager.load_and_enable_plugin("weather_plugin")
    logger.info(f"Enable load success: {load_res}")
    if not load_res:
        logger.error("PluginManager failed to hot-load and enable package!")
        return False
        
    # Verify starting hook executes
    active_ref = manager.active_plugins.get("weather_plugin")
    if not active_ref or active_ref["globals"].get("started") is not True:
        logger.error("on_start lifecycle callback was not invoked!")
        return False
        
    # Verify database registry status
    db_status = manager.registry.get_plugin_status("weather_plugin")
    logger.info(f"Database registry status: {db_status}")
    if db_status != "enabled":
        logger.error("Plugin status not logged to SQLite registry database!")
        return False
        
    manager.disable_plugin("weather_plugin")
    if "weather_plugin" in manager.active_plugins:
        logger.error("Plugin scope not deleted from active plugins catalog!")
        return False
    logger.info("Manager Hot-loading Lifecycles: [PASS]")

    # 5. Backup Updater & Rollback Safety
    logger.info("Testing version updating and rollback safety checking...")
    # Prepare updated version package
    manifest_data_upd = manifest_data.copy()
    manifest_data_upd["version"] = "2.0.0"
    with open(os.path.join(updated_src_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data_upd, f)
    with open(os.path.join(updated_src_dir, "main.py"), "w", encoding="utf-8") as f:
        f.write(plugin_code)

    upd_res = manager.updater.update_plugin("weather_plugin", updated_src_dir)
    logger.info(f"Update result success: {upd_res['success']}")
    if not upd_res["success"] or upd_res["manifest"].version != "2.0.0":
        logger.error("Plugin update upgrade failed!")
        return False
        
    # Test update failure trigger rollback
    # Create corrupted package missing main.py entry
    corrupted_dir = "logs/test_corrupted_src"
    os.makedirs(corrupted_dir, exist_ok=True)
    manifest_corrupted = manifest_data.copy()
    manifest_corrupted["version"] = "3.0.0"
    with open(os.path.join(corrupted_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_corrupted, f)
        
    upd_fail_res = manager.updater.update_plugin("weather_plugin", corrupted_dir)
    logger.info(f"Corrupted update result: {upd_fail_res}")
    if upd_fail_res["success"]:
        logger.error("Updater failed to catch corrupted plugin package!")
        return False
        
    # Verify folder rolled back to version 2.0.0
    active_manifest_path = os.path.join(workspace_dir, "weather_plugin", "manifest.json")
    with open(active_manifest_path, "r", encoding="utf-8") as f:
        chk_data = json.load(f)
    logger.info(f"Active manifest version after rollback check: {chk_data['version']}")
    if chk_data["version"] != "2.0.0":
        logger.error("Rollback failed to restore previous version data folder!")
        return False
    logger.info("Backup Updater & Rollbacks: [PASS]")

    # 6. Marketplace Local Listings
    logger.info("Testing local marketplace registries queries...")
    mkt = PluginMarketplace()
    results = mkt.search_marketplace("weather")
    logger.info(f"Marketplace search matches: {results}")
    if not results or results[0]["id"] != "weather_plugin":
        logger.error("Marketplace failed to locate weather plugin listing!")
        return False
    logger.info("Local Marketplace Listings: [PASS]")

    # Cleanup folders
    for path in (src_dir, updated_src_dir, corrupted_dir, workspace_dir):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                pass
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Plugin SDK (Phase G) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_plugin_sdk_pipeline()
    sys.exit(0 if success else 1)
