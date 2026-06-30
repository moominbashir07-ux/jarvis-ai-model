import logging
from typing import Dict, Any, Optional
from jarvis.agents.base_agent import BaseAgent
from jarvis.automation.sys_control import SystemController

logger = logging.getLogger("JARVIS.Agents.Automation")

class AutomationAgent(BaseAgent):
    """Executes keyboard, mouse, and system level commands on the Windows workspace."""

    def __init__(self, system_controller: Optional[SystemController] = None):
        super().__init__(
            name="AutomationAgent",
            description="Interfaces with the Windows SystemController to launch apps, clip boards, and edit files."
        )
        self.controller = system_controller or SystemController()
        self.controller.allow_unsafe = True

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"AutomationAgent executing task: '{task_description}'")
        context = context or {}
        action = context.get("action")
        
        try:
            if action == "create_file":
                filepath = context.get("filepath", "logs/output.txt")
                content = context.get("content", "")
                success, msg = self.controller.create_file(filepath, content)
                return {"success": success, "message": msg, "filepath": filepath}
                
            elif action == "delete_file":
                filepath = context.get("filepath")
                recycle = context.get("use_recycle_bin", True)
                success, msg = self.controller.delete_file_path(filepath, use_recycle_bin=recycle)
                return {"success": success, "message": msg}
                
            elif action == "write_clipboard":
                text = context.get("text", "")
                success, msg = self.controller.write_clipboard(text)
                return {"success": success, "message": msg}

            elif action == "open_browser" or action == "launch_website":
                url = context.get("url", "https://google.com")
                success, msg = self.controller.launch_website(url)
                return {"success": success, "message": msg}
                
            return {"success": False, "error": f"Unsupported automation action: '{action}'."}
        except Exception as e:
            logger.error(f"AutomationAgent tool execution failed: {e}")
            return {"success": False, "error": str(e)}
