import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger("JARVIS.Core.DepGraph")

class DependencyGraph:
    """Computes initialization order and flags circular references for core subsystems."""

    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = {}

    def add_service(self, name: str, deps: List[str]):
        """Declares dependency requirements for a specific service."""
        self.dependencies[name] = set(deps)

    def resolve_initialization_order(self) -> List[str]:
        """Calculates topological ordering using DFS, checking circular constraints."""
        visited: Set[str] = set()
        temp_mark: Set[str] = set()
        order: List[str] = []

        def visit(node: str):
            if node in temp_mark:
                logger.error(f"Circular dependency lock detected involving service: '{node}'!")
                raise RuntimeError(f"Circular dependency involving '{node}'")
            if node not in visited:
                temp_mark.add(node)
                for dep in self.dependencies.get(node, []):
                    visit(dep)
                temp_mark.remove(node)
                visited.add(node)
                order.append(node)

        for service in self.dependencies:
            if service not in visited:
                visit(service)

        logger.info(f"Topological initialization sequence resolved: {order}")
        return order
