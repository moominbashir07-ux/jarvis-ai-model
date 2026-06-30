import logging
from typing import List, Dict, Any
from jarvis.intelligence.behavior_tracker import BehaviorTracker
from jarvis.intelligence.workflow_detector import WorkflowDetector
from jarvis.intelligence.confidence_model import ConfidenceModel
from jarvis.intelligence.interruption_policy import InterruptionPolicy
from jarvis.intelligence.suggestion_engine import SuggestionEngine
from jarvis.intelligence.scheduler import BackgroundScheduler

logger = logging.getLogger("JARVIS.Intelligence.Engine")

class ProactiveEngine:
    """Production Facade coordinating behavior tracking, workflow detection, and policies enforcement."""

    def __init__(self, check_interval_sec: float = 10.0):
        self.tracker = BehaviorTracker()
        self.detector = WorkflowDetector()
        self.confidence = ConfidenceModel()
        self.policy = InterruptionPolicy()
        self.suggestions = SuggestionEngine(confidence_model=self.confidence)
        
        self.scheduler = BackgroundScheduler(
            check_callback=self.run_audit_cycle,
            interval_seconds=check_interval_sec
        )
        self.latest_suggestions: List[Dict[str, Any]] = []

    def start(self):
        """Activates periodic behavior tracking analysis."""
        self.scheduler.start()

    def run_audit_cycle(self, suppression_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Invokes behavioral checks, workflow parsing, and policy filters."""
        logger.info("Executing periodic proactive intelligence audit...")
        
        logs = self.tracker.get_logs()
        workflows = self.detector.analyze_sequence(logs)
        sugs = self.suggestions.generate_suggestions(workflows, logs)
        
        policy_context = suppression_context or {
            "is_fullscreen": False,
            "in_meeting": False,
            "cpu_load": 15.0
        }
        
        if self.policy.should_suppress(policy_context):
            logger.info("Interruption policy suppressed proactive suggestions.")
            self.latest_suggestions = []
            return []

        self.latest_suggestions = sugs
        return sugs

    def record_suggestion_feedback(self, suggestion_id: str, action: str):
        """Records user feedback logs (ACCEPT, REJECT, IGNORE) to adapt future weights."""
        logger.info(f"Recording feedback for Suggestion '{suggestion_id}': [{action}]")
        
        category = "workspace_prepare"
        if "outlook" in suggestion_id:
            category = "outlook_compose"
        elif "summarize" in suggestion_id:
            category = "research_summary"
            
        self.confidence.record_feedback(category, action)

    def stop(self):
        self.scheduler.stop()
