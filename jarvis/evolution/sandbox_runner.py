import os
import shutil
import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Evolution.SandboxRunner")

class SandboxRunner:
    """Prepares copy workspaces, deploys patch diff files, and checks compile statuses."""

    def __init__(self, sandbox_workspace: str):
        self.workspace = sandbox_workspace

    def deploy_and_verify(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """Copies target files to workspace, overrides lines, and checks compile syntax."""
        logger.info(f"Sandbox deployment initiated for patch: '{patch['patch_id']}'")
        os.makedirs(self.workspace, exist_ok=True)
        
        target_rel = patch["target_file"]
        sandbox_dest = os.path.join(self.workspace, target_rel)
        os.makedirs(os.path.dirname(sandbox_dest), exist_ok=True)

        try:
            logger.info("Running syntax validation checks...")
            
            with open(sandbox_dest, "w", encoding="utf-8") as f:
                f.write(patch["replacement_content"])
                
            with open(sandbox_dest, "r", encoding="utf-8") as f:
                code = f.read()
            compile(code, sandbox_dest, "exec")
            
            logger.info("Sandbox validation successful.")
            return {"success": True, "sandbox_path": sandbox_dest, "error": None}
        except Exception as e:
            logger.error(f"Sandbox syntax validation failed: {e}")
            return {"success": False, "sandbox_path": sandbox_dest, "error": str(e)}

    def cleanup(self):
        if os.path.exists(self.workspace):
            try:
                shutil.rmtree(self.workspace)
            except Exception:
                pass
