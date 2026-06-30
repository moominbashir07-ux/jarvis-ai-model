import logging
import json
import time
from typing import Dict, Any, Optional
from jarvis.agents.base_agent import BaseAgent
from jarvis.memory.memory_manager import MemoryManager

logger = logging.getLogger("JARVIS.Agents.Memory")

class MemoryAgent(BaseAgent):
    """Retrieves relevant database facts and stores task execution outcomes."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        super().__init__(
            name="MemoryAgent",
            description="Manages agent session context logs and preference checks in the database."
        )
        self.memory = memory_manager or MemoryManager()
        self.memory.initialize()

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"MemoryAgent handling operation: '{task_description}'")
        context = context or {}
        action = context.get("action", "read")
        key = context.get("key")

        try:
            if action == "read" and key:
                val = self.memory.db.execute("SELECT mem_value FROM memories WHERE mem_key = ?", (key,))
                result = val[0][0] if val else None
                return {"success": True, "value": result}
                
            elif action == "write" and key and "value" in context:
                self.memory.set_memory(
                    key=key,
                    value=str(context["value"]),
                    category=context.get("category", "general"),
                    importance=context.get("importance", 1)
                )
                return {"success": True, "msg": f"Saved fact: {key}"}
                
            return {"success": False, "error": "Invalid action or parameters."}
        except Exception as e:
            logger.error(f"MemoryAgent db transaction failed: {e}")
            return {"success": False, "error": str(e)}
