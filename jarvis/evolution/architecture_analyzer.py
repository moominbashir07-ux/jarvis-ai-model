import os
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Evolution.ArchAnalyzer")

class ArchitectureAnalyzer:
    """Inspects package imports lists to identify circular imports, coupling issues, or layer leaks."""

    def __init__(self):
        pass

    def check_circular_imports(self, files: List[str]) -> List[Dict[str, Any]]:
        """Scans import code strings to identify circular reference loops between modules."""
        logger.info("Analyzing package dependency tree for circular import coupling locks...")
        violations = []
        
        import_map = {}
        for filepath in files:
            name = os.path.basename(filepath).replace(".py", "")
            import_map[name] = []
            if not os.path.exists(filepath):
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        m = re.match(r"^(?:from|import)\s+([\w\.]+)", line)
                        if m:
                            imported = m.group(1).split(".")[-1]
                            import_map[name].append(imported)
            except Exception as e:
                logger.error(f"Failed to scan import lines in {filepath}: {e}")

        checked = set()
        for mod, imports in import_map.items():
            for imp in imports:
                if imp in import_map and mod in import_map[imp] and (imp, mod) not in checked:
                    violations.append({
                        "type": "circular_import",
                        "description": f"Direct circular import cycle detected: '{mod}' <=> '{imp}'",
                        "severity": "HIGH"
                    })
                    checked.add((mod, imp))
                    checked.add((imp, mod))
                    
        return violations
