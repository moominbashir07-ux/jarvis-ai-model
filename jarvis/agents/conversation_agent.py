import logging
from typing import Dict, Any
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Conversation")

class ConversationAgent(BaseAgent):
    """Maintains dialog context logs and speaks status updates to the user."""

    def __init__(self):
        super().__init__(
            name="ConversationAgent",
            description="Manages dialog briefs and verbal status updates."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"ConversationAgent expressing: '{task_description}'")
        return {
            "success": True,
            "speech_output": f"Spoken: {task_description}",
            "dialog_status": "COMPLETED"
        }
