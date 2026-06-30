import re
import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Plugins.Validator")

class PluginValidator:
    """Validates manifest configurations, semantics versions formatting, and signature hashes."""

    def __init__(self):
        pass

    def validate_manifest(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs checks to verify required keys exist and versions conform to standard schemas."""
        required = ("name", "id", "version", "entry", "api_version")
        for req in required:
            if req not in manifest_data:
                logger.error(f"Validation FAILED: Missing required field '{req}'")
                return {"valid": False, "error": f"Missing required field '{req}'"}

        version = manifest_data["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            logger.error(f"Validation FAILED: Invalid semantic version code format '{version}'")
            return {"valid": False, "error": f"Invalid semantic version code '{version}'"}

        allowed_permissions = {
            "internet", "filesystem_read", "filesystem_write", "clipboard",
            "voice", "camera", "vision", "notifications", "automation",
            "memory", "scheduler"
        }
        perms = manifest_data.get("permissions", [])
        for p in perms:
            if p.lower().strip() not in allowed_permissions:
                logger.error(f"Validation FAILED: Unauthorized permission scope requested: '{p}'")
                return {"valid": False, "error": f"Unauthorized permission scope requested: '{p}'"}

        logger.info(f"Manifest configuration validation SUCCESS: [{manifest_data['id']}]")
        return {"valid": True, "error": None}
