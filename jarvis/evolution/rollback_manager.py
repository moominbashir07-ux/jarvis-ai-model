import os
import shutil
import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Evolution.Rollback")

class RollbackManager:
    """Restores previous archived version files if validation benchmarks fail."""

    def __init__(self, backup_root: str):
        self.backup_root = backup_root

    def rollback_patch(self, patch: Dict[str, Any]) -> bool:
        """Restores previous script contents from backup directory."""
        logger.info(f"Initiating rollback sequence for patch: '{patch['patch_id']}'")
        
        target = patch["target_file"]
        backup_path = os.path.join(self.backup_root, f"{patch['patch_id']}_original")

        try:
            if os.path.exists(backup_path):
                if os.path.exists(target):
                    os.remove(target)
                shutil.copy2(backup_path, target)
                logger.info(f"Successfully rolled back patch: '{patch['patch_id']}'")
                return True
            else:
                logger.warning(f"No backup archive snapshot found for patch '{patch['patch_id']}'. Aborting rollback.")
                return False
        except Exception as e:
            logger.error(f"Rollback execution failed: {e}")
            return False
