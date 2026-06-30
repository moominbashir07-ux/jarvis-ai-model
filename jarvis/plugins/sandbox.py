import logging
from typing import Dict, Any, Callable

logger = logging.getLogger("JARVIS.Plugins.Sandbox")

class PluginSandbox:
    """Executes plugin code blocks inside an import-redacted global scope dictionary wrapper."""

    def __init__(self, plugin_id: str, permission_manager: Any):
        self.plugin_id = plugin_id
        self.permissions = permission_manager

    def execute_code(self, code: str, api_instance: Any) -> Dict[str, Any]:
        """Runs the code inside a restricted context dictionary."""
        logger.info(f"Preparing sandbox execution environment for plugin: '{self.plugin_id}'")
        
        def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
            dangerous_libs = ("os", "sys", "subprocess", "ctypes", "win32api", "win32gui", "win32process")
            if name in dangerous_libs:
                if name == "os" and self.permissions.verify_permission(self.plugin_id, "filesystem_read"):
                    import os
                    return os
                raise ImportError(f"Import of dangerous module '{name}' blocked by sandbox security policy.")
            return __import__(name, globals, locals, fromlist, level)

        # Define clean builtins mapping
        clean_builtins = {
            "print": print,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "len": len,
            "ImportError": ImportError,
            "eval": None,
            "exec": None,
            "__import__": restricted_import
        }

        restricted_globals = {
            "__builtins__": clean_builtins,
            "jarvis_api": api_instance
        }

        try:
            compiled = compile(code, f"<sandbox_{self.plugin_id}>", "exec")
            # Execute compiled code inside restricted sandbox namespace
            exec(compiled, restricted_globals)
            
            on_start = restricted_globals.get("on_start")
            on_stop = restricted_globals.get("on_stop")
            
            return {
                "success": True,
                "globals": restricted_globals,
                "on_start": on_start,
                "on_stop": on_stop,
                "error": None
            }
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {
                "success": False,
                "globals": {},
                "on_start": None,
                "on_stop": None,
                "error": str(e)
            }
class_name = "PluginSandbox"
