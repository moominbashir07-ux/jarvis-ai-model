import logging
from typing import Dict, Any, List
from jarvis.distributed.node_registry import NodeRegistry
from jarvis.distributed.node_discovery import NodeDiscovery
from jarvis.distributed.leader_election import LeaderElection
from jarvis.distributed.replication_engine import ReplicationEngine
from jarvis.distributed.conflict_resolver import ConflictResolver
from jarvis.distributed.distributed_memory import DistributedMemory
from jarvis.distributed.distributed_event_bus import DistributedEventBus
from jarvis.distributed.distributed_scheduler import DistributedScheduler
from jarvis.distributed.remote_executor import RemoteExecutor
from jarvis.distributed.security_manager import SecurityManager
from jarvis.distributed.cloud_connector import CloudConnector
from jarvis.distributed.mobile_gateway import MobileGateway
from jarvis.distributed.api_gateway import APIGateway
from jarvis.distributed.cluster_dashboard import ClusterDashboard
from jarvis.distributed.distributed_diagnostics import DistributedDiagnostics

logger = logging.getLogger("JARVIS.Distributed.Orchestrator")

class DistributedOrchestrator:
    """Coordinating facade linking nodes registry discoveries, replication engines, and TLS executors."""

    def __init__(self, node_id: str, db_path: str = "jarvis_memory.db"):
        self.node_id = node_id
        
        self.registry = NodeRegistry(db_path=db_path)
        self.discovery = NodeDiscovery()
        self.election = LeaderElection(node_id)
        
        self.replication = ReplicationEngine()
        self.resolver = ConflictResolver()
        self.memory = DistributedMemory(self.replication, self.resolver)
        
        self.event_bus = DistributedEventBus()
        self.scheduler = DistributedScheduler()
        self.executor = RemoteExecutor()
        self.security = SecurityManager()
        
        self.cloud = CloudConnector()
        self.mobile = MobileGateway()
        self.api = APIGateway()
        
        self.dashboard = ClusterDashboard()
        self.diagnostics = DistributedDiagnostics()

    def discover_and_register_nodes(self) -> List[Dict[str, Any]]:
        """Invokes discovery scans and records profiles to database."""
        logger.info("Starting subnet discovery sequences...")
        nodes = self.discovery.discover_local_nodes()
        
        for n in nodes:
            self.registry.register_node(
                node_id=n["node_id"],
                name=n["name"],
                node_type=n["type"],
                ip=n["ip"],
                cpu=n["cpu_cores"],
                ram=n["ram_mb"]
            )
            
        return self.registry.get_active_nodes()

    def run_cluster_sync_cycle(self) -> bool:
        """Pushes queued database transactions logs to discovered peer lists."""
        logger.info("Executing periodic database synchronization sweep...")
        active = self.registry.get_active_nodes()
        return self.replication.synchronize_peers(active)
