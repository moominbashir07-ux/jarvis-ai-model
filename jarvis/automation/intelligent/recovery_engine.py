import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("JARVIS.Automation.Recovery")

class RecoveryEngine:
    """Detects popup blockers and resolves alternate automation strategies."""

    def __init__(self):
        pass

    def check_modal_blockers(self, active_windows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identifies dialog boxes or access denied popups in visible window logs."""
        for win in active_windows:
            title = win.get("title", "").lower()
            if "error" in title or "warning" in title or "confirm" in title or "save" in title:
                logger.info(f"Modal popup blocker detected: '{win['title']}'")
                return win
        return None

    def get_recovery_action(self, failed_action: Dict[str, Any]) -> Dict[str, Any]:
        """Formulates alternate strategies (e.g. replacing a click with hotkey shortcuts)."""
        logger.info(f"Formulating recovery action for failed step: '{failed_action['id']}'")
        
        if failed_action["type"] == "CLICK_CONTROL" and failed_action["target"] == "Save":
            recovery = {
                "id": f"{failed_action['id']}_recovery",
                "type": "SHORTCUT",
                "target": "Ctrl+Shift+S",
                "reason": "Bypassing click failure with save hotkey shortcut.",
                "confidence": 0.90
            }
            logger.info(f"Recovery strategy: Keyboard Shortcut {recovery['target']}")
            return recovery
            
        return {
            "id": f"{failed_action['id']}_fallback",
            "type": "SHORTCUT",
            "target": "Escape",
            "reason": "Escaping blocked dialogue.",
            "confidence": 0.80
        }
