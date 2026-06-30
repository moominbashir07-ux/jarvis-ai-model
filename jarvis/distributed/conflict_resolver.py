import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Distributed.Resolver")

class ConflictResolver:
    """Resolves data sync anomalies using timestamps or incremental version vectors."""

    def __init__(self):
        pass

    def resolve_conflict(self, local_item: Dict[str, Any], incoming_item: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves overlapping keys using Last-Write-Wins (LWW) timestamp comparisons."""
        local_ts = local_item.get("timestamp", 0.0)
        incoming_ts = incoming_item.get("timestamp", 0.0)

        if incoming_ts > local_ts:
            logger.info(f"Sync conflict resolved: incoming item overrides local (incoming: {incoming_ts} > local: {local_ts})")
            return incoming_item
        else:
            logger.info("Sync conflict resolved: local item overrides incoming.")
            return local_item
