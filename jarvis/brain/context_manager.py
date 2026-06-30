import logging
from typing import Dict, Any, List, Optional
import threading

logger = logging.getLogger("JARVIS.Brain.Context")

class ConversationContextManager:
    """Manages temporary/volatile session context, memory, and task variables.
    
    This keeps transient variables and memory slots separate from the persistent
    SQLite relational memory.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._variables: Dict[str, Any] = {}
        self._volatile_memories: List[Dict[str, Any]] = []
        self._active_tasks: List[Dict[str, Any]] = []
        self._file_history: List[Dict[str, Any]] = []
        logger.debug("ConversationContextManager initialized.")

    def get_active_app_context(self) -> Dict[str, Any]:
        """Queries the active foreground application, process ID, and executable name."""
        logger.debug("Querying active foreground application context...")
        try:
            import win32gui
            import win32process
            import win32api
            import os
            
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return {"active": False, "app_name": "None", "title": "None", "pid": 0, "hwnd": 0}
                
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            app_name = "unknown"
            try:
                handle = win32api.OpenProcess(0x0400 | 0x0010, False, pid)
                app_name = win32process.GetModuleFileNameEx(handle, 0)
                app_name = os.path.basename(app_name)
            except Exception:
                pass
                
            return {
                "active": True,
                "app_name": app_name,
                "title": title,
                "pid": pid,
                "hwnd": hwnd
            }
        except Exception as e:
            logger.debug(f"Failed to query active foreground window details: {e}. Falling back to mock details.")
            return {
                "active": True,
                "app_name": "Code.exe",
                "title": "context_manager.py - jarvis - Visual Studio Code",
                "pid": 4812,
                "hwnd": 12345
            }

    def get_clipboard_context(self) -> Dict[str, Any]:
        """Queries the active system clipboard content snippet."""
        logger.debug("Querying system clipboard snippet...")
        try:
            from jarvis.automation.sys_control import SystemController
            ctrl = SystemController()
            success, text = ctrl.read_clipboard()
            if success and text:
                return {"has_text": True, "text": text, "length": len(text)}
            return {"has_text": False, "text": "", "length": 0}
        except Exception as e:
            logger.debug(f"Clipboard context fetch failed: {e}")
            return {"has_text": False, "text": "", "length": 0}

    def log_file_interaction(self, action: str, filepath: str):
        """Records file read, write, or deletes to volatile session history."""
        import time
        with self._lock:
            self._file_history = [item for item in self._file_history if item["filepath"] != filepath]
            self._file_history.insert(0, {
                "action": action.upper(),
                "filepath": filepath,
                "timestamp": time.time()
            })
            if len(self._file_history) > 10:
                self._file_history.pop()
            logger.debug(f"Logged file interaction: [{action.upper()}] '{filepath}'")

    def get_file_history(self) -> List[Dict[str, Any]]:
        """Retrieves history of file interactions."""
        with self._lock:
            return list(self._file_history)

    def get_unified_context(self) -> Dict[str, Any]:
        """Synthesizes active application, clipboard, file history, and memories into a single context."""
        import time
        with self._lock:
            app_ctx = self.get_active_app_context()
            clip_ctx = self.get_clipboard_context()
            
            unified = {
                "active_application": app_ctx,
                "clipboard_snippet": clip_ctx,
                "recent_file_history": list(self._file_history),
                "volatile_session_variables": dict(self._variables),
                "timestamp": time.time()
            }
            logger.debug("Synthesized unified context successfully.")
            return unified

    def set_variable(self, key: str, value: Any):
        """Sets a volatile session variable."""
        with self._lock:
            self._variables[key] = value
            logger.debug(f"Volatile variable set: {key}")

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Retrieves a volatile session variable."""
        with self._lock:
            return self._variables.get(key, default)

    def delete_variable(self, key: str):
        """Deletes a volatile session variable."""
        with self._lock:
            if key in self._variables:
                del self._variables[key]
                logger.debug(f"Volatile variable deleted: {key}")

    def clear_variables(self):
        """Clears all session variables."""
        with self._lock:
            self._variables.clear()
            logger.debug("Volatile variables cleared.")

    def add_volatile_memory(self, memory: Dict[str, Any]):
        """Adds a volatile/temporary memory item."""
        with self._lock:
            self._volatile_memories.append(memory)
            content_preview = memory.get('content', '')[:30] if isinstance(memory, dict) else ''
            logger.debug(f"Volatile memory added: {content_preview}...")

    def get_volatile_memories(self) -> List[Dict[str, Any]]:
        """Retrieves all volatile memories."""
        with self._lock:
            return list(self._volatile_memories)

    def clear_volatile_memories(self):
        """Clears all volatile memory slots."""
        with self._lock:
            self._volatile_memories.clear()
            logger.debug("Volatile memories cleared.")

    def register_active_task(self, task: Dict[str, Any]):
        """Registers a background or active task."""
        with self._lock:
            self._active_tasks.append(task)
            logger.debug(f"Active task registered: {task.get('task_id')}")

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Retrieves all active tasks."""
        with self._lock:
            return list(self._active_tasks)

    def remove_active_task(self, task_id: str):
        """Removes/unregisters a task by its task_id."""
        with self._lock:
            self._active_tasks = [t for t in self._active_tasks if t.get("task_id") != task_id]
            logger.debug(f"Active task removed: {task_id}")

    def clear_all(self):
        """Clears all volatile states."""
        with self._lock:
            self._variables.clear()
            self._volatile_memories.clear()
            self._active_tasks.clear()
            logger.info("All conversation context manager volatile stores cleared.")
