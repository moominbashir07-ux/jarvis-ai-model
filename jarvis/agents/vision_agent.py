import logging
from typing import Dict, Any, Optional
from jarvis.agents.base_agent import BaseAgent
from jarvis.vision.vision_manager import VisionManager

logger = logging.getLogger("JARVIS.Agents.Vision")

class VisionAgent(BaseAgent):
    """Interfaces with the VisionManager to read screen elements and confirm UI states."""

    def __init__(self, vision_manager: Optional[VisionManager] = None):
        super().__init__(
            name="VisionAgent",
            description="Performs OCR inspections and retrieves element coordinates on active displays."
        )
        self.vision = vision_manager or VisionManager()
        self.vision.enabled = True

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"VisionAgent executing task: '{task_description}'")
        context = context or {}
        action = context.get("action", "locate_text")
        
        try:
            if action == "locate_text":
                target = context.get("target_text", "Save")
                found, x, y = self.vision.locate_text_on_screen(target)
                return {"success": True, "found": found, "x": x, "y": y}
                
            elif action == "analyze_screenshot":
                filepath = context.get("filepath", "logs/screen.png")
                success, path, text = self.vision.capture_and_analyze_screen(filepath)
                return {"success": success, "filepath": path, "text": text}
                
            return {"success": False, "error": f"Unsupported vision action: '{action}'."}
        except Exception as e:
            logger.error(f"VisionAgent perception task failed: {e}")
            return {"success": False, "error": str(e)}
