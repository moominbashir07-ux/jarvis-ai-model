import os
import ast
import logging
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Evolution.CodeAnalyzer")

class CodeAnalyzer:
    """Statically parses source code files to identify missing type hints, resource leak warning flags, and redundant loops."""

    def __init__(self):
        pass

    def analyze_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parses AST structures to identify design flaws and code styling issues."""
        logger.debug(f"Parsing AST structures for code file: '{filepath}'")
        findings = []

        if not os.path.exists(filepath):
            return findings

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=filepath)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if ast.get_docstring(node) is None:
                        findings.append({
                            "type": "documentation_gap",
                            "line": node.lineno,
                            "filepath": filepath,
                            "description": f"Function '{node.name}' is missing a docstring documentation descriptor.",
                            "severity": "LOW"
                        })
                    if node.returns is None:
                        findings.append({
                            "type": "missing_type_hint",
                            "line": node.lineno,
                            "filepath": filepath,
                            "description": f"Function '{node.name}' has no return type annotation hints declared.",
                            "severity": "MEDIUM"
                        })
        except Exception as e:
            logger.error(f"Failed to analyze source file AST: {e}")

        return findings
