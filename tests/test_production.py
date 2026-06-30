import os
import sys
import time
import logging
from pathlib import Path
from jarvis.core.logger import setup_logger
from jarvis.core.updater import AutoUpdater
from jarvis.core.watchdog import ProcessWatchdog
from jarvis.core.telemetry import TelemetryTracker
from jarvis.core.health_manager import HealthManager
from jarvis.agents.registry import agent_registry
from package_jarvis import package_app

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestProduction")

def test_production_readiness():
    logger.info("--- Starting Production Hardening & RC1 Verification ---")

    logger.info("Verifying application packaging and environment validation...")
    build_success = package_app()
    logger.info(f"Packaging validator execution status: {build_success}")
    if not build_success:
        logger.error("Application packaging check failed!")
        return False

    logger.info("Testing Auto-Updater update payload check and cryptographic signing...")
    updater = AutoUpdater(current_version="1.0.0")
    
    update_info = updater.check_for_updates()
    logger.info(f"Update Check result: {update_info}")
    if not update_info["has_update"] or update_info["latest_version"] != "1.0.1":
        logger.error("Auto updater check returned unexpected version parameters!")
        return False

    valid_sig = updater.validate_manifest(update_info["manifest"])
    logger.info(f"Signature signature checks valid: {valid_sig}")
    if not valid_sig:
        logger.error("Manifest cryptographic signature verification failed!")
        return False

    logger.info("Simulating failed write operations to verify recovery rollbacks...")
    fail_payload = {
        "latest_version": "1.0.1",
        "simulate_fail": True
    }
    apply_success, msg = updater.apply_update(fail_payload)
    logger.info(f"Rollback response: {apply_success} | message: {msg}")
    if not apply_success or "Rollback complete" not in msg:
        logger.error("Update recovery rollback failed to restore previous version!")
        return False

    logger.info("Testing Telemetry privacy configuration controls...")
    telemetry = TelemetryTracker(is_enabled=True)
    
    telemetry.record_event("test_latency_event", 0.125, {"detail": "success"})
    if len(telemetry.metrics_log) != 1:
        logger.error("Failed to record telemetry logs when enabled!")
        return False
        
    telemetry.set_telemetry_opt(enabled=False)
    telemetry.record_event("test_latency_event_disabled", 0.05)
    logger.info(f"Telemetry logs size after disabled: {len(telemetry.metrics_log)}")
    if len(telemetry.metrics_log) != 1:
        logger.error("Recorded telemetry events after user opted out!")
        return False

    logger.info("Testing ProcessWatchdog interception and recovery resets...")
    watchdog = ProcessWatchdog()
    
    logger.info("Injecting simulated backend process crash to verify watchdog recovery...")
    recovered = watchdog.recover_subsystem("backend_thread")
    logger.info(f"Watchdog recovery status: {recovered}")
    if not recovered:
        logger.error("Watchdog failed to restore subsystem thread-safe context!")
        return False

    watchdog.handle_global_exception(ValueError, ValueError("Mock System Crash"), None)
    logger.info(f"Watchdog crash log audit: {watchdog.crashed_subsystems}")
    if "backend_thread" not in watchdog.crashed_subsystems:
        logger.error("Watchdog did not record thread exception event history!")
        return False
    watchdog.shutdown()

    logger.info("Testing HealthManager CPU, RAM, active agents, and device checks...")
    health = HealthManager()
    status_report = health.get_status_report()
    logger.info(f"Enhanced Health Status Report:\n{status_report}")
    
    performance = status_report.get("performance", {})
    devices = status_report.get("devices", {})
    if "cpu_utilization_percent" not in performance or "ram_utilization_percent" not in performance:
        logger.error("Health report missing resource metrics!")
        return False
    if devices.get("microphone") != "ONLINE" or devices.get("speaker") != "ONLINE":
        logger.error("Health report mic/speaker hardware flags degraded!")
        return False

    logger.info("Production Hardening & RC1 Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS Production Hardening Tests       ")
    logger.info("==========================================")
    
    success = test_production_readiness()
    sys.exit(0 if success else 1)
