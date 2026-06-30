import os
import sys
import logging
from jarvis.core.logger import setup_logger
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
from jarvis.distributed.distributed_orchestrator import DistributedOrchestrator

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestDistributed")

def test_distributed_runtime_pipeline():
    logger.info("==========================================")
    logger.info("    Distributed Runtime (Phase 19) Test   ")
    logger.info("==========================================")

    db_path = "logs/test_distributed_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # Setup orchestrator facade
    orchestrator = DistributedOrchestrator(node_id="primary_desktop_node", db_path=db_path)

    # 1. Node Discovery & NodeRegistry SQLite registration
    logger.info("Testing cluster node discovery and database registrations...")
    nodes = orchestrator.discover_and_register_nodes()
    logger.info(f"Registered online nodes: {nodes}")
    if len(nodes) != 2:
        logger.error("NodeRegistry failed to index discovered nodes list!")
        return False
    logger.info("Node Discovery & Registry: [PASS]")

    # 2. Raft-style Leader Election
    logger.info("Testing Raft-style leader election quorum...")
    election_success = orchestrator.election.start_election(nodes)
    logger.info(f"Election promotion status: {election_success}")
    if not election_success or orchestrator.election.leader_id != "primary_desktop_node":
        logger.error("LeaderElection failed to elect local node as leader!")
        return False
    logger.info("Leader Election: [PASS]")

    # 3. Distributed Memory updates & Conflict Resolution (LWW)
    logger.info("Testing Last-Write-Wins (LWW) conflict resolver...")
    # Seed local database entry
    orchestrator.memory.update_key("user_name", "Initial Name", timestamp=100.0)
    
    # Simulate newer incoming conflict write
    orchestrator.memory.update_key("user_name", "Updated Name", timestamp=105.0)
    logger.info(f"Current Memory Store: {orchestrator.memory.memory_store['user_name']}")
    if orchestrator.memory.memory_store["user_name"]["value"] != "Updated Name":
        logger.error("ConflictResolver failed to override key using Last-Write-Wins timestamp!")
        return False
        
    # Simulate older incoming conflict write (should be skipped)
    orchestrator.memory.update_key("user_name", "Stale Name", timestamp=99.0)
    if orchestrator.memory.memory_store["user_name"]["value"] != "Updated Name":
        logger.error("ConflictResolver incorrectly overrode key with older timestamp!")
        return False
    logger.info("Distributed Memory & Conflict Resolution: [PASS]")

    # 4. Synchronize replication events
    logger.info("Testing replication synchronizations across followers...")
    sync_success = orchestrator.run_cluster_sync_cycle()
    logger.info(f"Sync execution: {sync_success}")
    if not sync_success:
        logger.error("Replication sync cycle failed!")
        return False
    logger.info("Memory Replication: [PASS]")

    # 5. Distributed Event Bus routing
    logger.info("Testing distributed event bus subscriptions...")
    received_payload = {}
    def on_broadcast(payload):
        nonlocal received_payload
        received_payload = payload
        
    orchestrator.event_bus.subscribe("CLUSTER_ALERT", on_broadcast)
    orchestrator.event_bus.publish_event("CLUSTER_ALERT", {"alert": "critical_low_battery"}, nodes)
    logger.info(f"Received bus payload: {received_payload}")
    if received_payload.get("alert") != "critical_low_battery":
        logger.error("EventBus failed to distribute notification frames!")
        return False
    logger.info("Event Bus: [PASS]")

    # 6. Distributed Scheduler & Remote Executor
    logger.info("Testing capacity-based scheduling and remote executors...")
    task_payload = {"task_name": "compile_sandbox_code"}
    optimal_node = orchestrator.scheduler.select_optimal_node(task_payload, nodes)
    logger.info(f"Optimal node selected: {optimal_node}")
    if optimal_node["node_id"] != "mac_worker_1":
        logger.error("DistributedScheduler failed to select node with highest capacity (CPU/RAM)!")
        return False
        
    exec_res = orchestrator.executor.execute_remote_task(task_payload, optimal_node)
    logger.info(f"Executor result: {exec_res}")
    if not exec_res["success"]:
        logger.error("RemoteExecutor failed to run task!")
        return False
    logger.info("Scheduler & Remote Executor: [PASS]")

    # 7. TLS Secure connection manager
    logger.info("Testing TLS authentication and encryption payloads...")
    # Validate node with correct token
    auth_ok = orchestrator.security.authenticate_node("mac_worker_1", "valid_cluster_handshake_token_123")
    if not auth_ok:
        logger.error("SecurityManager rejected valid connection handshake token!")
        return False
        
    # Validate node with bad token
    auth_bad = orchestrator.security.authenticate_node("mac_worker_1", "bad_token")
    if auth_bad:
        logger.error("SecurityManager accepted invalid connection handshake token!")
        return False
        
    cipher = orchestrator.security.encrypt_payload("sensitive_api_key")
    plain = orchestrator.security.decrypt_payload(cipher)
    if plain != "sensitive_api_key":
        logger.error("SecurityManager decryption payload content mismatch!")
        return False
    logger.info("TLS Security: [PASS]")

    # 8. Mobile & Cloud Connectors
    logger.info("Testing cloud workers offloads and mobile companion streams...")
    mobile_ok = orchestrator.mobile.handle_mobile_connection("ios_phone_client")
    if not mobile_ok or not orchestrator.mobile.stream_active:
        logger.error("MobileGateway failed to establish session stream!")
        return False
        
    cloud_res = orchestrator.cloud.offload_task_to_cloud({"task_name": "llm_inference"})
    if not cloud_res["success"]:
        logger.error("CloudConnector failed to delegate workload to worker pools!")
        return False
    logger.info("Cloud & Mobile Gateways: [PASS]")

    # 9. Dashboard stats summaries & Connection Diagnostics
    logger.info("Testing cluster health summaries and connection diagnostics audits...")
    dash_sum = orchestrator.dashboard.get_dashboard_summary(nodes)
    if dash_sum["active_nodes_count"] != 2:
        logger.error("ClusterDashboard reported incorrect active nodes count!")
        return False
        
    diag_res = orchestrator.diagnostics.run_diagnostics()
    if diag_res["packet_loss_percent"] != 0.0:
        logger.error("DistributedDiagnostics reported incorrect packet loss!")
        return False
    logger.info("Dashboards & Diagnostics: [PASS]")

    # Cleanup DB
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Distributed Intelligence (Phase 19) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_distributed_runtime_pipeline()
    sys.exit(0 if success else 1)
