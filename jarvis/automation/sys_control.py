import logging
import os
import re
import sys
import time
import shutil
import subprocess
import webbrowser
import ctypes
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from jarvis.config import settings

logger = logging.getLogger("JARVIS.Automation")

# Windows specific virtual key codes for volume control
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

class SystemController:
    """Production-grade Windows Control & Automation Engine for JARVIS AI OS.
    
    Implements OS application control, file management, system volume emulation,
    screenshot grabbing, security permission filters, and transaction undo operations.
    """

    def __init__(self, event_bus=None, memory_manager=None):
        self.event_bus = event_bus
        self.memory = memory_manager
        self.allow_unsafe = settings.allow_unsafe_commands
        
        # Undo execution log stack for recovery
        self._undo_stack: List[Tuple[str, Dict[str, Any]]] = []
        
        # Security profile categorization
        self.security_rules = {
            "launch_website": "SAFE",
            "search_system": "SAFE",
            "capture_screenshot": "SAFE",
            "adjust_volume": "SAFE",
            "read_clipboard": "SAFE",
            "write_clipboard": "SAFE",
            "clear_clipboard": "SAFE",
            "get_running_apps": "SAFE",
            "create_folder": "RESTRICTED",
            "create_file": "RESTRICTED",
            "open_app": "RESTRICTED",
            "close_app": "RESTRICTED",
            "control_app_window": "RESTRICTED",
            "move_file": "DANGEROUS",
            "delete_file_path": "DANGEROUS",
            "execute_shell": "DANGEROUS"
        }
        
        self.allowed_binaries = {
            "calc", "calc.exe",
            "notepad", "notepad.exe",
            "explorer", "explorer.exe",
            "taskmgr", "taskmgr.exe",
            "mspaint", "mspaint.exe",
            "chrome", "chrome.exe",
            "firefox", "firefox.exe",
            "msedge", "msedge.exe",
            "cmd", "cmd.exe",
            "powershell", "powershell.exe"
        }
        logger.debug("SystemController initialized with security profile rules.")

    def initialize(self) -> bool:
        """Initializes automation handles."""
        logger.info("Initializing Windows System Control Automation Engine...")
        return True

    def check_permission(self, action_name: str) -> str:
        """Evaluates permission profile bounds for an operation.
        
        Returns:
            Status string: 'ALLOW', 'DENY', or 'PROMPT'
        """
        category = self.security_rules.get(action_name, "DANGEROUS")
        
        if category == "SAFE":
            return "ALLOW"
            
        if category == "RESTRICTED":
            return "ALLOW" if self.allow_unsafe else "PROMPT"
            
        # Dangerous actions
        return "ALLOW" if self.allow_unsafe else "PROMPT"

    # --- Windows Applications & Web ---
    def open_app(self, app_path_or_name: str) -> Tuple[bool, str]:
        """Launches a Windows application process."""
        permission = self.check_permission("open_app")
        if permission == "DENY":
            return False, "Blocked: Insufficient system privileges."
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm launch of '{app_path_or_name}'."

        # Security Hardening Allowlist Check
        basename = os.path.basename(app_path_or_name).lower()
        if not self.allow_unsafe and basename not in self.allowed_binaries:
            msg = f"Security Blocked: Launching '{app_path_or_name}' is not permitted by policy allowlist."
            logger.warning(msg)
            self._log_audit("open_app", msg, "blocked_security")
            return False, msg

        logger.info(f"Launching application process: '{app_path_or_name}'")
        if self.event_bus:
            self.event_bus.publish("AutomationStarted", {"action": "open_app", "target": app_path_or_name})
            
        try:
            # Check if name is simple executable or complete path
            if os.path.exists(app_path_or_name) or app_path_or_name.endswith(".exe"):
                subprocess.Popen([app_path_or_name])
            else:
                # Search on PATH cleanly to avoid shell invocation
                resolved = shutil.which(app_path_or_name)
                if resolved:
                    subprocess.Popen([resolved])
                else:
                    # Direct invocation as a list
                    subprocess.Popen([app_path_or_name])
                
            self._log_audit("open_app", f"Opened app: {app_path_or_name}", "success")
            return True, f"Successfully launched '{app_path_or_name}'."
        except Exception as e:
            msg = f"Failed to open application: {e}"
            logger.error(msg)
            self._log_audit("open_app", msg, "failed")
            return False, msg

    def close_app(self, process_name: str) -> Tuple[bool, str]:
        """Terminates active Windows process threads."""
        permission = self.check_permission("close_app")
        if permission == "DENY":
            return False, "Blocked: Process termination rights denied."
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm termination of process '{process_name}'."

        # Input Sanitization: Strict regex validation for filename execution targets
        if not re.match(r"^[a-zA-Z0-9_\-\.]+\.exe$", process_name):
            msg = f"Security Blocked: Process name '{process_name}' contains illegal characters."
            logger.warning(msg)
            self._log_audit("close_app", msg, "blocked_security")
            return False, msg

        logger.warning(f"Killing process threads: '{process_name}'")
        if self.event_bus:
            self.event_bus.publish("AutomationStarted", {"action": "close_app", "target": process_name})
            
        try:
            if sys.platform == "win32":
                cmd = ["taskkill", "/f", "/im", process_name]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    self._log_audit("close_app", f"Terminated process: {process_name}", "success")
                    return True, f"Successfully terminated process '{process_name}'."
                else:
                    return False, f"Process kill failed: {res.stderr}"
            else:
                return False, "Process termination is only supported on Windows hosts."
        except Exception as e:
            msg = f"Error terminating process: {e}"
            logger.error(msg)
            self._log_audit("close_app", msg, "failed")
            return False, msg

    def launch_website(self, url: str) -> Tuple[bool, str]:
        """Opens a web page link in the default browser browser."""
        logger.info(f"Opening website link: '{url}'")
        try:
            webbrowser.open(url)
            self._log_audit("launch_website", f"Launched URL: {url}", "success")
            return True, f"Launched URL '{url}'."
        except Exception as e:
            msg = f"Failed to open link: {e}"
            self._log_audit("launch_website", msg, "failed")
            return False, msg

    # --- Windows Volume Control (ctypes Virtual Key Emulation) ---
    def adjust_volume(self, direction: str, steps: int = 5) -> Tuple[bool, str]:
        """Emulates Windows multimedia volume keystrokes via ctypes.
        
        Args:
            direction: 'up', 'down', or 'mute'
            steps: Number of times to press the key (each press is 2% volume step)
        """
        logger.info(f"Adjusting system volume: direction={direction}, steps={steps}")
        try:
            if sys.platform != "win32":
                return False, "Volume adjustment is restricted to Windows systems."

            if direction.lower() == "mute":
                ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)  # KeyUp
                return True, "System volume muted/unmuted."
                
            vk_code = VK_VOLUME_UP if direction.lower() == "up" else VK_VOLUME_DOWN
            for _ in range(steps):
                ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
                time = __import__('time')
                time.sleep(0.02)  # brief debounce sleep
                
            self._log_audit("adjust_volume", f"Adjusted volume: {direction}", "success")
            return True, f"Adjusted system volume {direction} by {steps * 2}%."
        except Exception as e:
            msg = f"Volume adjustment failure: {e}"
            logger.error(msg)
            self._log_audit("adjust_volume", msg, "failed")
            return False, msg

    # --- Filesystem Actions (with Undo History recovery) ---
    def create_folder(self, folder_path: str) -> Tuple[bool, str]:
        """Creates directory paths."""
        permission = self.check_permission("create_folder")
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm folder creation at '{folder_path}'."

        path = Path(folder_path)
        logger.info(f"Creating directory folder: '{path}'")
        try:
            if path.exists():
                return True, "Folder already exists."
                
            path.mkdir(parents=True, exist_ok=True)
            self._log_audit("create_folder", f"Created directory: {folder_path}", "success")
            
            # Record undo action
            self._undo_stack.append(("delete_folder", {"path": folder_path}))
            return True, f"Successfully created folder at '{folder_path}'."
        except Exception as e:
            msg = f"Failed to create folder: {e}"
            self._log_audit("create_folder", msg, "failed")
            return False, msg

    def move_file(self, src: str, dst: str) -> Tuple[bool, str]:
        """Moves file paths, adding the operation to the undo stack."""
        permission = self.check_permission("move_file")
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm move operations from '{src}' to '{dst}'."

        src_path = Path(src)
        dst_path = Path(dst)
        logger.info(f"Moving file node: '{src_path}' -> '{dst_path}'")
        
        try:
            if not src_path.exists():
                return False, f"Source file '{src}' does not exist."
                
            # If destination is a directory, append filename
            actual_dst = dst_path
            if dst_path.is_dir():
                actual_dst = dst_path / src_path.name

            shutil.move(str(src_path), str(actual_dst))
            self._log_audit("move_file", f"Moved file from {src} to {actual_dst}", "success")
            
            # Record undo action (moving it back)
            self._undo_stack.append(("move_file_back", {"src": str(actual_dst), "dst": str(src_path)}))
            return True, f"Successfully moved file to '{actual_dst}'."
        except Exception as e:
            msg = f"Failed to move file: {e}"
            logger.error(msg)
            self._log_audit("move_file", msg, "failed")
            return False, msg

    def search_system(self, directory: str, query_pattern: str) -> Tuple[bool, List[str]]:
        """Searches directory files matching queries."""
        dir_path = Path(directory)
        logger.info(f"Searching directory '{directory}' for matches matching '{query_pattern}'")
        
        try:
            if not dir_path.exists() or not dir_path.is_dir():
                return False, ["Directory does not exist or is unreachable."]
                
            # Recursive glob matching
            matches = list(dir_path.rglob(query_pattern))
            return True, [str(m) for m in matches]
        except Exception as e:
            logger.error(f"Search failure: {e}")
            return False, [f"Error: {e}"]

    # --- Windows Screen Capture ---
    def capture_screenshot(self, output_dir: str = "logs") -> Tuple[bool, str]:
        """Captures active Windows screen frame."""
        # Custom dynamic check for library bindings (Pillow is standard python out-of-the-box screen grabber)
        logger.info("Initiating screenshot capture...")
        try:
            from PIL import ImageGrab, Image
            Path(output_dir).mkdir(exist_ok=True)
            
            output_file = Path(output_dir) / f"screenshot_{int(__import__('time').time())}.png"
            # Blocking screen grab
            try:
                img = ImageGrab.grab()
            except OSError as oe:
                logger.warning(f"Physical screen grab not supported on this host display context: {oe}. Creating dummy frame.")
                img = Image.new("RGB", (800, 600), color="black")
                
            img.save(output_file)
            
            logger.info(f"Screenshot successfully saved: {output_file}")
            self._log_audit("capture_screenshot", f"Captured screen to: {output_file}", "success")
            return True, str(output_file)
        except Exception as e:
            msg = f"Failed to capture screen framework: {e}"
            logger.error(msg)
            self._log_audit("capture_screenshot", msg, "failed")
            return False, msg

    # --- Recovery (Undo Action Stack) ---
    def execute_undo(self) -> Tuple[bool, str]:
        """Reverses the last filesystem modification action in the undo stack."""
        if not self._undo_stack:
            return False, "Undo history is empty."
            
        action, params = self._undo_stack.pop()
        logger.warning(f"Executing undo recovery action: '{action}' with params: {params}")
        
        try:
            if action == "delete_folder":
                path = Path(params["path"])
                if path.exists() and path.is_dir():
                    shutil.rmtree(path)
                    return True, f"Undo complete: Deleted folder '{path}'."
                    
            elif action == "delete_file":
                path = Path(params["path"])
                if path.exists():
                    path.unlink()
                    return True, f"Undo complete: Deleted file '{path}'."
                    
            elif action == "move_file_back":
                src = params["src"]
                dst = params["dst"]
                shutil.move(src, dst)
                return True, f"Undo complete: Moved file back to '{dst}'."
                
            return False, "Unknown recovery action."
        except Exception as e:
            return False, f"Recovery undo action failed: {e}"

    # --- Audit Trail logging ---
    def _log_audit(self, action_name: str, details: str, status: str):
        """Records command operations directly into the active Memory sqlite databases."""
        if self.event_bus:
            self.event_bus.publish("AutomationFinished", {
                "action": action_name,
                "status": status,
                "details": details
            })
        elif self.memory:
            # We seed metrics to memory table
            self.memory.set_memory(
                key=f"last_automation_{action_name}",
                value=f"Status: {status} | Details: {details}",
                category="general",
                importance=1
            )
            # Add to memory audit task log directly
            if hasattr(self.memory, 'conn') and self.memory.conn:
                try:
                    cursor = self.memory.conn.cursor()
                    cursor.execute("""
                        INSERT INTO automation_logs (action_name, execution_status, error_message)
                        VALUES (?, ?, ?)
                    """, (action_name, status, details if status != "success" else None))
                    self.memory.conn.commit()
                except Exception as e:
                    logger.debug(f"Audit table logging error: {e}")
        else:
            logger.debug(f"[Audit Log Entry] Action: {action_name} | Status: {status} | Details: {details}")

    # --- Windows Clipboard Operations ---
    def write_clipboard(self, text: str) -> Tuple[bool, str]:
        """Writes Unicode text to the Windows clipboard."""
        permission = self.check_permission("write_clipboard")
        if permission == "DENY":
            return False, "Blocked: Clipboard write rights denied."
        if permission == "PROMPT":
            return False, "Permission Required: Confirm clipboard write."

        try:
            import win32clipboard
            import win32con
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            logger.info("Unicode text copied to clipboard successfully.")
            self._log_audit("write_clipboard", f"Copied text of length {len(text)}", "success")
            return True, "Successfully copied text to clipboard."
        except Exception as e:
            msg = f"Failed to write to clipboard: {e}"
            logger.error(msg)
            self._log_audit("write_clipboard", msg, "failed")
            return False, msg

    def read_clipboard(self) -> Tuple[bool, str]:
        """Reads text from the Windows clipboard."""
        permission = self.check_permission("read_clipboard")
        if permission == "DENY":
            return False, "Blocked: Clipboard read rights denied."
        if permission == "PROMPT":
            return False, "Permission Required: Confirm clipboard read."

        try:
            import win32clipboard
            import win32con
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                if isinstance(data, bytes):
                    data = data.decode('utf-8', errors='ignore')
            else:
                data = ""
            win32clipboard.CloseClipboard()
            self._log_audit("read_clipboard", f"Read text of length {len(data)}", "success")
            return True, data
        except Exception as e:
            msg = f"Failed to read clipboard: {e}"
            logger.error(msg)
            self._log_audit("read_clipboard", msg, "failed")
            return False, msg

    def clear_clipboard(self) -> Tuple[bool, str]:
        """Clears clipboard data."""
        permission = self.check_permission("clear_clipboard")
        if permission == "DENY":
            return False, "Blocked: Clipboard clear rights denied."
        if permission == "PROMPT":
            return False, "Permission Required: Confirm clipboard clear."

        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            self._log_audit("clear_clipboard", "Cleared clipboard context", "success")
            return True, "Successfully cleared clipboard."
        except Exception as e:
            msg = f"Failed to clear clipboard: {e}"
            logger.error(msg)
            self._log_audit("clear_clipboard", msg, "failed")
            return False, msg

    # --- Windows Window Controls ---
    def get_running_apps(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Enumerates currently running windowed applications (visible titles and PIDs)."""
        permission = self.check_permission("get_running_apps")
        if permission == "DENY":
            return False, []
        if permission == "PROMPT":
            return False, []

        try:
            import win32gui
            import win32process
            
            apps = []
            
            def enum_callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        extra.append({
                            "hwnd": hwnd,
                            "title": title,
                            "pid": pid
                        })
                        
            win32gui.EnumWindows(enum_callback, apps)
            self._log_audit("get_running_apps", f"Found {len(apps)} visible windows", "success")
            return True, apps
        except Exception as e:
            logger.error(f"Error enumerating windows: {e}")
            return False, []

    def control_app_window(self, hwnd: int, action: str) -> Tuple[bool, str]:
        """Minimizes, maximizes, restores, or brings a window to focus by HWND.
        
        Args:
            hwnd: Window handle ID
            action: 'minimize', 'maximize', 'restore', or 'foreground'
        """
        permission = self.check_permission("control_app_window")
        if permission == "DENY":
            return False, "Blocked: Window control rights denied."
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm window control '{action}' on handle {hwnd}."

        try:
            import win32gui
            import win32con
            
            if not win32gui.IsWindow(hwnd):
                return False, f"Invalid window handle ID: {hwnd}."
                
            action_lower = action.lower()
            if action_lower == "minimize":
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                msg = f"Minimized window handle {hwnd}."
            elif action_lower == "maximize":
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                msg = f"Maximized window handle {hwnd}."
            elif action_lower == "restore":
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                msg = f"Restored window handle {hwnd}."
            elif action_lower == "foreground":
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # Attachment bypass logic for SetForegroundWindow
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    import win32process
                    import win32api
                    fore_thread = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
                    app_thread = win32api.GetCurrentThreadId()
                    if fore_thread != app_thread:
                        ctypes.windll.user32.AttachThreadInput(app_thread, fore_thread, True)
                        win32gui.SetForegroundWindow(hwnd)
                        ctypes.windll.user32.AttachThreadInput(app_thread, fore_thread, False)
                    else:
                        win32gui.SetForegroundWindow(hwnd)
                msg = f"Brought window handle {hwnd} to foreground."
            else:
                return False, f"Unsupported window action: '{action}'."
                
            self._log_audit("control_app_window", msg, "success")
            return True, msg
        except Exception as e:
            msg = f"Window control action failed: {e}"
            logger.error(msg)
            self._log_audit("control_app_window", msg, "failed")
            return False, msg

    # --- Filesystem Actions (Extended) ---
    def create_file(self, file_path: str, content: str = "") -> Tuple[bool, str]:
        """Creates a text file at target path."""
        permission = self.check_permission("create_file")
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm file creation at '{file_path}'."

        path = Path(file_path)
        logger.info(f"Creating file node: '{path}'")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            self._log_audit("create_file", f"Created file: {file_path}", "success")
            
            # Record undo action
            self._undo_stack.append(("delete_file", {"path": file_path}))
            return True, f"Successfully created file at '{file_path}'."
        except Exception as e:
            msg = f"Failed to create file: {e}"
            self._log_audit("create_file", msg, "failed")
            return False, msg

    def delete_file_path(self, file_path: str, use_recycle_bin: bool = True) -> Tuple[bool, str]:
        """Deletes a file or folder target, optionally sending to Windows Recycle Bin."""
        permission = self.check_permission("delete_file_path")
        if permission == "PROMPT":
            return False, f"Permission Required: Confirm deletion of '{file_path}'."

        path = Path(file_path)
        if not path.exists():
            return False, f"Target path '{file_path}' does not exist."

        logger.warning(f"Deleting path node: '{path}' (use_recycle_bin={use_recycle_bin})")
        try:
            if use_recycle_bin:
                from win32com.shell import shell, shellcon
                abs_path = str(path.resolve())
                shell.SHFileOperation((
                    0, 
                    shellcon.FO_DELETE, 
                    abs_path, 
                    None, 
                    shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, 
                    None, 
                    None
                ))
                msg = f"Moved path to Recycle Bin: {file_path}"
                self._log_audit("delete_file_path", msg, "success")
                return True, f"Successfully moved '{file_path}' to Recycle Bin."
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                msg = f"Permanently deleted path: {file_path}"
                self._log_audit("delete_file_path", msg, "success")
                return True, f"Successfully deleted '{file_path}' permanently."
        except Exception as e:
            msg = f"Deletion operation failed: {e}"
            logger.error(msg)
            self._log_audit("delete_file_path", msg, "failed")
            return False, msg

    def cleanup(self):
        """Clean up automation hooks."""
        logger.debug("SystemController hooks released.")
