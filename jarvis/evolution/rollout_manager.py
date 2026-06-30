import os
import shutil
import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Evolution.Rollout")

class RolloutManager:
    """Safely updates target production file structures, keeping previous copies archived."""

    def __init__(self, backup_root: str):
        self.backup_root = backup_root

    def deploy_patch(self, patch: Dict[str, Any]) -> bool:
        """Copies replacement strings to target and archives a backup snapshot."""
        logger.info(f"Applying rollout patch: '{patch['patch_id']}'")
        
        target = patch["target_file"]
        backup_path = os.path.join(self.backup_root, f"{patch['patch_id']}_original")
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        try:
            if os.path.exists(target):
                shutil.copy2(target, backup_path)
                logger.info(f"Archived previous snapshot copy to: '{backup_path}'")
            
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(patch["replacement_content"])
                
            logger.info(f"Rollout patch successfully deployed: '{patch['patch_id']}'")
            return True
        except Exception as e:
            logger.error(f"Rollout deployment failed: {e}")
            return False
