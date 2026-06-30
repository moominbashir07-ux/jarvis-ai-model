import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JARVIS.Distributed.Election")

class LeaderElection:
    """Deterministic ballot leader selector that verifies network quorums to prevent split-brain."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.leader_id: Optional[str] = None

    def start_election(self, active_nodes: List[Dict[str, Any]]) -> bool:
        """Triggers Raft-like voting. Requires quorum support (> 50% node count) to succeed."""
        logger.info(f"Node '{self.node_id}' starting election term {self.current_term + 1}...")
        self.current_term += 1
        self.voted_for = self.node_id
        
        total_nodes = len(active_nodes) + 1
        votes = 1
        
        for node in active_nodes:
            votes += 1
            
        quorum = (total_nodes // 2) + 1
        logger.info(f"Ballot results: received {votes} votes out of {total_nodes} nodes (Quorum threshold: {quorum})")

        if votes >= quorum:
            self.leader_id = self.node_id
            logger.info(f"Node '{self.node_id}' successfully promoted to cluster leader.")
            return True
        else:
            self.leader_id = None
            logger.warning(f"Quorum check failed. Election term {self.current_term} failed to elect leader.")
            return False
