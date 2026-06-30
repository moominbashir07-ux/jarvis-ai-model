import os
import sys
import logging
from jarvis.core.logger import setup_logger
from jarvis.core.lifecycle import RuntimeLifecycle
from jarvis.runtime.runtime import UnifiedRuntime
from jarvis.runtime.runtime_loop import RuntimeMasterLoop
from jarvis.runtime.runtime_controller import RuntimeController
from jarvis.runtime.service_initializer import ServiceInitializer
from jarvis.runtime.module_connector import ModuleConnector
from jarvis.runtime.session_manager import SessionManager
from jarvis.runtime.request_router import RequestRouter
from jarvis.runtime.conversation_pipeline import ConversationPipeline
from jarvis.runtime.execution_pipeline import ExecutionPipeline
from jarvis.runtime.context_pipeline import ContextPipeline
from jarvis.runtime.shutdown_controller import ShutdownController
from jarvis.runtime.runtime_metrics import RuntimeMetrics
from jarvis.runtime.runtime_validator import RuntimeValidator

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestRuntime")

def test_runtime_integration_pipeline():
    logger.info("==========================================")
    logger.info("     Unified Runtime (Phase 21) Test      ")
    logger.info("==========================================")

    db_path = "logs/test_unified_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # Instantiation
    runtime = UnifiedRuntime(db_path=db_path)

    # 1. Cold Boot sequence
    logger.info("Testing UnifiedRuntime cold boot sequence...")
    if runtime.lifecycle != RuntimeLifecycle.INITIALIZING:
        logger.error("UnifiedRuntime lifecycle did not start as INITIALIZING!")
        return False
        
    boot_ok = runtime.cold_boot()
    logger.info(f"Cold boot status: {boot_ok}")
    if not boot_ok or runtime.lifecycle != RuntimeLifecycle.RUNNING:
        logger.error("UnifiedRuntime cold boot failed or lifecycle state is not RUNNING!")
        return False
    logger.info("Cold Boot: [PASS]")

    # 2. Connection binds & Registry Validator
    logger.info("Testing registry connector validations...")
    valid_ok = runtime.validator.validate_runtime_integrity()
    logger.info(f"Validator status: {valid_ok}")
    if not valid_ok:
        logger.error("RuntimeValidator failed to verify active service registries running state!")
        return False
    logger.info("Validator assertions: [PASS]")

    # 3. Master Loop single execution cycle
    logger.info("Testing RuntimeMasterLoop single execution cycle...")
    loop = RuntimeMasterLoop(runtime)
    cycle_res = loop.execute_single_cycle(b"MOCK_USER_MICROPHONE_AUDIO_INPUT")
    logger.info(f"Cycle execution results: {cycle_res}")
    
    if cycle_res["transcription"] != "Run web server calculation":
        logger.error("MasterLoop transcription mismatch!")
        return False
    if cycle_res["verification_status"] != "verified" or cycle_res["tts_audio_bytes_length"] <= 0:
        logger.error("MasterLoop workflow execution or vocal response synthesis failed!")
        return False
    logger.info("Master iteration loop: [PASS]")

    # 4. Controller Restarts & Recoveries
    logger.info("Testing RuntimeController restarts and emergency recoveries...")
    controller = RuntimeController(runtime)
    
    restart_ok = controller.warm_restart()
    logger.info(f"Warm restart status: {restart_ok}")
    if not restart_ok or runtime.lifecycle != RuntimeLifecycle.RUNNING:
        logger.error("RuntimeController warm restart boot sequence failed!")
        return False
        
    rec_ok = controller.emergency_recovery()
    logger.info(f"Emergency recovery status: {rec_ok}")
    if not rec_ok or runtime.lifecycle != RuntimeLifecycle.RUNNING:
        logger.error("RuntimeController emergency recovery boot sequence failed!")
        return False
    logger.info("Restarts & Recoveries: [PASS]")

    # 5. Latency metrics retrieval
    logger.info("Testing metrics latency retrieval stats...")
    stats = runtime.metrics.retrieve_latency_metrics()
    logger.info(f"Latency stats: {stats}")
    if stats["cold_boot_ms"] != 420.0 or stats["runtime_memory_mb"] != 450.0:
        logger.error("RuntimeMetrics returned incorrect latency statistics!")
        return False
    logger.info("Latency metrics: [PASS]")

    # 6. Graceful Shutdown sequence
    logger.info("Testing UnifiedRuntime graceful shutdown sequence...")
    shutdown_ok = runtime.graceful_shutdown()
    logger.info(f"Graceful shutdown status: {shutdown_ok}")
    if not shutdown_ok or runtime.lifecycle != RuntimeLifecycle.SHUTDOWN:
        logger.error("Graceful shutdown failed or lifecycle state is not SHUTDOWN!")
        return False
    logger.info("Graceful Shutdown: [PASS]")

    # Cleanup DB
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Unified Runtime (Phase 21) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_runtime_integration_pipeline()
    sys.exit(0 if success else 1)
