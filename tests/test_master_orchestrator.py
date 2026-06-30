import os
import sys
import logging
from jarvis.core.logger import setup_logger
from jarvis.core.lifecycle import RuntimeLifecycle
from jarvis.core.dependency_graph import DependencyGraph
from jarvis.core.service_registry import ServiceRegistry
from jarvis.core.event_router import EventRouter
from jarvis.core.state_manager import GlobalStateManager
from jarvis.core.resource_manager import ResourceManager
from jarvis.core.health_monitor import HealthMonitor
from jarvis.core.runtime_database import RuntimeDatabase
from jarvis.core.startup_manager import StartupManager
from jarvis.core.shutdown_manager import ShutdownManager
from jarvis.core.diagnostics import DiagnosticsEngine
from jarvis.core.telemetry import TelemetryTracker
from jarvis.core.master_orchestrator import MasterOrchestrator
from jarvis.core.runtime_manager import RuntimeManager

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestMasterOrchestrator")

def test_master_orchestrator_pipeline():
    logger.info("==========================================")
    logger.info("    Master Orchestrator (Phase 18) Test   ")
    logger.info("==========================================")

    db_path = "logs/test_runtime_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # 1. Dependency Graph sorting & Circular locks
    logger.info("Testing topological dependency graph ordering...")
    graph = DependencyGraph()
    graph.add_service("A", ["B"])
    graph.add_service("B", [])
    order = graph.resolve_initialization_order()
    logger.info(f"Topological sorting resolved: {order}")
    if order != ["B", "A"]:
        logger.error("DependencyGraph topological sorting returned incorrect order!")
        return False
        
    # Check circular references validation
    graph_cycle = DependencyGraph()
    graph_cycle.add_service("X", ["Y"])
    graph_cycle.add_service("Y", ["X"])
    try:
        graph_cycle.resolve_initialization_order()
        logger.error("DependencyGraph failed to catch circular references loop!")
        return False
    except RuntimeError:
        logger.info("Circular dependency correctly detected: [PASS]")

    # 2. MasterOrchestrator Cold Boot sequence
    logger.info("Testing MasterOrchestrator cold boot sequence...")
    orchestrator = MasterOrchestrator(db_path=db_path)
    if orchestrator.lifecycle != RuntimeLifecycle.INITIALIZING:
        logger.error("MasterOrchestrator lifecycle state did not start as INITIALIZING!")
        return False
        
    boot_success = orchestrator.cold_boot()
    logger.info(f"Cold boot status: {boot_success}")
    if not boot_success or orchestrator.lifecycle != RuntimeLifecycle.RUNNING:
        logger.error("Cold boot sequence failed or lifecycle state is not RUNNING!")
        return False
    logger.info("Cold Boot Sequence: [PASS]")

    # 3. Service Registry lookups
    logger.info("Testing ServiceRegistry registry catalog lookups...")
    instance = orchestrator.registry.lookup_service("MemoryService")
    logger.info(f"Subsystem lookup: {instance}")
    if instance != "MockInstance_MemoryService":
        logger.error("ServiceRegistry returned incorrect mock instance reference!")
        return False
    logger.info("Service Registry: [PASS]")

    # 4. Global State Manager updates
    logger.info("Testing StateManager variables updates...")
    orchestrator.state_manager.update_state("voice_pipeline_active", True)
    val = orchestrator.state_manager.get_state("voice_pipeline_active")
    if val is not True:
        logger.error("StateManager failed to store state parameters!")
        return False
    logger.info("StateManager State registers: [PASS]")

    # 5. Thread-safe Event Routing pub/sub
    logger.info("Testing event router pub/sub broadcast transfer...")
    received_payload = {}
    def on_event_fired(payload):
        nonlocal received_payload
        received_payload = payload
        
    orchestrator.event_router.subscribe("TEST_EVENT", on_event_fired)
    orchestrator.event_router.publish("TEST_EVENT", {"status": "event_triggered"})
    logger.info(f"Received event payload: {received_payload}")
    if received_payload.get("status") != "event_triggered":
        logger.error("EventRouter failed to broadcast event payload to sub-listeners!")
        return False
    logger.info("Event Router: [PASS]")

    # 6. Health Monitor perform scans
    logger.info("Testing health monitor diagnostic audits...")
    health_res = orchestrator.health_monitor.perform_health_audit()
    logger.info(f"Health verification report: {health_res}")
    if health_res["status"] != "healthy":
        logger.error("Health monitor failed to verify active service registries!")
        return False
    logger.info("Health Monitor: [PASS]")

    # 7. Hardware Resource manager CPU checks
    logger.info("Testing Resource manager CPU footprint scans...")
    res_metrics = orchestrator.resource_manager.check_system_resources()
    logger.info(f"Resource metrics: {res_metrics}")
    if res_metrics["cpu_utilization_percent"] != 15.4:
        logger.error("ResourceManager returned incorrect hardware utilization values!")
        return False
    logger.info("Resource Manager: [PASS]")

    # 8. Warm Restarts and Recoveries
    logger.info("Testing RuntimeManager restarts and emergency recoveries...")
    run_mgr = RuntimeManager(orchestrator)
    
    warm_success = run_mgr.warm_restart()
    logger.info(f"Warm restart success: {warm_success}")
    if not warm_success or orchestrator.lifecycle != RuntimeLifecycle.RUNNING:
        logger.error("Warm restart re-boot sequence failed!")
        return False
        
    rec_success = run_mgr.emergency_recovery()
    logger.info(f"Emergency recovery success: {rec_success}")
    if not rec_success or orchestrator.lifecycle != RuntimeLifecycle.RUNNING:
        logger.error("Emergency recovery re-boot sequence failed!")
        return False
    logger.info("Runtime Restarts & Recoveries: [PASS]")

    # 9. Graceful Shutdown sequence
    logger.info("Testing MasterOrchestrator graceful shutdown sequences...")
    shutdown_success = orchestrator.graceful_shutdown()
    logger.info(f"Graceful shutdown success: {shutdown_success}")
    if not shutdown_success or orchestrator.lifecycle != RuntimeLifecycle.SHUTDOWN:
        logger.error("Graceful shutdown failed or lifecycle state is not SHUTDOWN!")
        return False
    logger.info("Graceful Shutdown: [PASS]")

    # Cleanup DB
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Master System Orchestrator (Phase 18) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_master_orchestrator_pipeline()
    sys.exit(0 if success else 1)
