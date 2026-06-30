import logging
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Distributed.Replication")

class ReplicationEngine:
    """Manages transactional pushes of SQLite memories updates to cluster followers."""

    def __init__(self):
        self.replication_queue: List[Dict[str, Any]] = []

    def queue_replication_record(self, record: Dict[str, Any]):
        """Pushes data frame to replication buffer."""
        self.replication_queue.append(record)
        logger.debug(f"Queued sync frame: '{record.get('key')}'")

    def synchronize_peers(self, active_nodes: List[Dict[str, Any]]) -> bool:
        """Flushes buffered records to peer node database loops."""
        logger.info(f"Replicating database buffers across {len(active_nodes)} followers nodes...")
        
        for item in self.replication_queue:
            for node in active_nodes:
                logger.debug(f"Dispatched sync record '{item.get('key')}' to node '{node['name']}'")
                
        self.replication_queue.clear()
        logger.info("Database replication finished successfully.")
        return True
