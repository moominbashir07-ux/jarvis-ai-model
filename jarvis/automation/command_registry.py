import logging
import re
import urllib.parse
from typing import Dict, Any, Tuple, Optional, Callable

logger = logging.getLogger("JARVIS.Automation.CommandRegistry")

class CommandRegistry:
    """Registry that maps voice and text intents to Windows automation actions and generates spoken feedback."""

    def __init__(self, system_controller):
        self.sys_control = system_controller
        self._commands = {}
        self._register_default_commands()

    def register(self, command_name: str, pattern: str, handler: Callable[[re.Match], Tuple[bool, str]]):
        """Registers a command regex pattern and handler function."""
        self._commands[command_name] = {
            "pattern": re.compile(pattern, re.IGNORECASE),
            "handler": handler
        }
        logger.debug(f"Registered command pattern: {command_name} -> {pattern}")

    def _register_default_commands(self):
        # 1. Open Windows Settings
        self.register(
            "open_settings",
            r"(?:open|launch|show)\s+(?:windows\s+)?settings",
            self._handle_open_settings
        )
        # 2. Open Calculator
        self.register(
            "open_calculator",
            r"(?:open|launch|run)\s+(?:the\s+)?(?:calc|calculator)",
            self._handle_open_calc
        )
        # 3. Open Chrome
        self.register(
            "open_chrome",
            r"(?:open|launch|run)\s+(?:google\s+)?chrome",
            self._handle_open_chrome
        )
        # 4. Open Task Manager
        self.register(
            "open_taskmgr",
            r"(?:open|launch|show)\s+(?:the\s+)?(?:task\s+manager|taskmgr)",
            self._handle_open_taskmgr
        )
        # 5. Open Notepad
        self.register(
            "open_notepad",
            r"(?:open|launch|run)\s+(?:the\s+)?(?:notepad|text\s+editor)",
            self._handle_open_notepad
        )
        # 6. Open Paint
        self.register(
            "open_paint",
            r"(?:open|launch|run)\s+(?:the\s+)?(?:paint|mspaint)",
            self._handle_open_paint
        )
        # 7. Search Google
        self.register(
            "search_google",
            r"(?:search|google|lookup)\s+(?:google\s+for\s+|for\s+)?(.+)",
            self._handle_search_google
        )
        # 8. Search YouTube
        self.register(
            "search_youtube",
            r"(?:search\s+youtube\s+for\s+|youtube\s+for\s+|search\s+on\s+youtube\s+for\s+)(.+)",
            self._handle_search_youtube
        )
        # 9. Search Wikipedia
        self.register(
            "search_wikipedia",
            r"(?:search\s+wikipedia\s+for\s+|wikipedia\s+for\s+|search\s+on\s+wikipedia\s+for\s+)(.+)",
            self._handle_search_wikipedia
        )
        # 10. Launch Website
        self.register(
            "launch_website",
            r"(?:open|go\s+to|launch|visit)\s+website\s+(https?://\S+|www\.\S+|\S+\.\w{2,})",
            self._handle_launch_website
        )

    def execute(self, text: str) -> Optional[Tuple[bool, str]]:
        """Matches input against registered commands.
        
        Returns:
            Tuple: (success: bool, spoken_feedback: str) if matched, else None
        """
        cleaned_text = text.strip()
        for name, cmd in self._commands.items():
            match = cmd["pattern"].match(cleaned_text)
            if match:
                logger.info(f"CommandRegistry matched command [{name}] for input: '{cleaned_text}'")
                try:
                    success, feedback = cmd["handler"](match)
                    return success, feedback
                except Exception as e:
                    logger.error(f"Error executing command handler for {name}: {e}")
                    return False, f"I encountered an error trying to execute the action: {str(e)}"
        return None

    # --- Command Handlers ---
    def _handle_open_settings(self, match: re.Match) -> Tuple[bool, str]:
        success, msg = self.sys_control.open_app("ms-settings:")
        if not success:
            import webbrowser
            try:
                webbrowser.open("ms-settings:")
                return True, "Opening Windows Settings."
            except Exception as e:
                return False, f"Failed to open settings: {e}"
        return success, "Opening Windows Settings."

    def _handle_open_calc(self, match: re.Match) -> Tuple[bool, str]:
        success, msg = self.sys_control.open_app("calc.exe")
        return success, "Opening Calculator."

    def _handle_open_chrome(self, match: re.Match) -> Tuple[bool, str]:
        success, msg = self.sys_control.open_app("chrome.exe")
        if not success:
            import webbrowser
            try:
                webbrowser.open("https://www.google.com")
                return True, "Chrome process not found in path, launching default web browser instead."
            except:
                pass
        return success, "Opening Google Chrome."

    def _handle_open_taskmgr(self, match: re.Match) -> Tuple[bool, str]:
        success, msg = self.sys_control.open_app("taskmgr.exe")
        return success, "Opening Task Manager."

    def _handle_open_notepad(self, match: re.Match) -> Tuple[bool, str]:
        success, msg = self.sys_control.open_app("notepad.exe")
        return success, "Opening Notepad."

    def _handle_open_paint(self, match: re.Match) -> Tuple[bool, str]:
        success, msg = self.sys_control.open_app("mspaint.exe")
        return success, "Opening Paint."

    def _handle_search_google(self, match: re.Match) -> Tuple[bool, str]:
        query = match.group(1).strip()
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        success, msg = self.sys_control.launch_website(url)
        return success, f"Searching Google for {query}."

    def _handle_search_youtube(self, match: re.Match) -> Tuple[bool, str]:
        query = match.group(1).strip()
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        success, msg = self.sys_control.launch_website(url)
        return success, f"Searching YouTube for {query}."

    def _handle_search_wikipedia(self, match: re.Match) -> Tuple[bool, str]:
        query = match.group(1).strip()
        encoded_query = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}"
        success, msg = self.sys_control.launch_website(url)
        return success, f"Searching Wikipedia for {query}."

    def _handle_launch_website(self, match: re.Match) -> Tuple[bool, str]:
        url = match.group(1).strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        success, msg = self.sys_control.launch_website(url)
        return success, f"Launching website: {url}."
