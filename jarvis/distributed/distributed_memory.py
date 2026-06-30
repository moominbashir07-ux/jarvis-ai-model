import logging
from typing import Dict, Any
from jarvis.distributed.replication_engine import ReplicationEngine
from jarvis.distributed.conflict_resolver import ConflictResolver

logger = logging.getLogger("JARVIS.Distributed.Memory")

class DistributedMemory:
    """Consolidated memory interface replicating updates to sibling nodes."""

    def __init__(self, replication: ReplicationEngine, resolver: ConflictResolver):
        self.replication = replication
        self.resolver = resolver
        self.memory_store: Dict[str, Any] = {}

    def update_key(self, key: str, value: Any, timestamp: float):
        """Updates internal memory store state and buffers replication event."""
        incoming = {"key": key, "value": value, "timestamp": timestamp}
        
        if key in self.memory_store:
            local = self.memory_store[key]
            resolved = self.resolver.resolve_conflict(local, incoming)
            self.memory_store[key] = resolved
        else:
            self.memory_store[key] = incoming

        self.replication.queue_replication_record(self.memory_store[key])
        logger.debug(f"Memory update queued: '{key}' => '{value}'")
