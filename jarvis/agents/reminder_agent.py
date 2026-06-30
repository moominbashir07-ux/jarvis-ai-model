import logging
import threading
import time
from typing import Dict, Any, Optional
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Reminder")

class ReminderAgent(BaseAgent):
    """Autonomous Reminder Agent for JARVIS AI OS.
    
    Spawns background timer threads and speaks alerts when they expire.
    """

    def __init__(self, tts=None):
        super().__init__(
            name="ReminderAgent",
            description="Manages alarms and alerts users using Text-to-Speech."
        )
        self.tts = tts
        self.active_timers = []

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Setting reminder: '{task_description}'")
        
        # Determine delay
        delay = 2.0  # default 2s for testing
        try:
            if "second" in task_description:
                words = task_description.split()
                for i, w in enumerate(words):
                    if "second" in w and i > 0:
                        delay = float(words[i-1])
        except Exception:
            pass

        alert_message = (context or {}).get("message", f"Reminder alert: {task_description}")
        
        # Spawn asynchronous timer thread
        timer_thread = threading.Thread(
            target=self._run_timer,
            args=(delay, alert_message),
            daemon=True
        )
        timer_thread.start()
        
        self.active_timers.append({
            "message": alert_message,
            "delay": delay,
            "thread": timer_thread
        })
        
        return {
            "success": True,
            "reminder_text": alert_message,
            "delay_seconds": delay
        }

    def _run_timer(self, delay: float, message: str):
        """Timer countdown worker thread."""
        logger.info(f"Countdown started: {delay}s for reminder: '{message}'")
        time.sleep(delay)
        
        # Fire reminder alarm
        logger.warning(f"Reminder Alert Triggered: '{message}'")
        if self.tts:
            self.tts.speak(f"Sir, this is a reminder: {message}")
        else:
            print(f"\n⏰ [ALARM]: \"{message}\"\n")

    def cleanup(self):
        logger.debug("ReminderAgent cleanup completed.")
