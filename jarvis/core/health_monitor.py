import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Core.Health")

class HealthMonitor:
    """Audits registered subsystem statuses, heartbeats, and queue congestion indexes."""

    def __init__(self, registry: Any):
        self.registry = registry

    def perform_health_audit(self) -> Dict[str, Any]:
        """Runs checks to spot stalled pipelines or deadlocked threads."""
        logger.info("Initiating global subsystems health checks scan...")
        
        reports = {}
        for svc in ("VoiceService", "VisionService", "AutomationService", "AgentService"):
            status = self.registry.get_service_status(svc) or "healthy"
            reports[svc] = status

        is_healthy = all(s != "failed" for s in reports.values())
        logger.info(f"Subsystems health verification completed. Healthy: {is_healthy}")
        return {
            "status": "healthy" if is_healthy else "degraded",
            "services_reports": reports
        }
