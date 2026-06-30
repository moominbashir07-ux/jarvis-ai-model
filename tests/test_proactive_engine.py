import sys
import logging
from jarvis.core.logger import setup_logger
from jarvis.intelligence.proactive_engine import ProactiveEngine

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestProactiveEngine")

def test_proactive_intelligence():
    logger.info("==========================================")
    logger.info("  Proactive Intelligence Engine Test      ")
    logger.info("==========================================")

    engine = ProactiveEngine()

    # 1. Privacy Redactions
    logger.info("Testing sensitive credentials and API key redactions...")
    secret_text = "My key is sk-1234567890abcdef1234567890abcdef1234567890abcdef"
    redacted = engine.tracker.redact_string(secret_text)
    logger.info(f"Redacted text: '{redacted}'")
    if "[REDACTED_SENSITIVE_KEY]" not in redacted:
        logger.error("API key was not masked!")
        return False
        
    secret_field = {"api_key": "sk-1234567890abcdef1234567890abcdef1234567890abcdef", "safe_field": "public"}
    redacted_fields = engine.tracker.redact_sensitive_fields(secret_field)
    logger.info(f"Redacted dict: {redacted_fields}")
    if redacted_fields["api_key"] == "sk-1234567890abcdef1234567890abcdef1234567890abcdef":
        logger.error("API key field was not masked!")
        return False
    logger.info("Privacy Redaction: [PASS]")

    # 2. Behavior Tracking & Workflow Detection (Scenario 1)
    logger.info("Testing behavior logs tracking and repetitive sequence switches...")
    # Simulate a sequence: Code -> Terminal -> Chrome, Code -> Terminal -> Chrome (Frequency = 2)
    t = 100.0
    for _ in range(2):
        engine.tracker.log_event("APP_SWITCH", {"app_name": "Code.exe", "timestamp": t})
        engine.tracker.log_event("APP_SWITCH", {"app_name": "Terminal.exe", "timestamp": t+2})
        engine.tracker.log_event("APP_SWITCH", {"app_name": "Chrome.exe", "timestamp": t+4})
        t += 10.0
        
    logs = engine.tracker.get_logs()
    logger.info(f"Behavior Logs logged: {len(logs)}")
    if len(logs) != 6:
        logger.error("Not all app switches logged!")
        return False
        
    # Analyze workflows
    workflows = engine.detector.analyze_sequence(logs)
    logger.info(f"Detected Workflows count: {len(workflows)}")
    if not workflows or workflows[0]["frequency"] != 2:
        logger.error("Repetitive workspace switches sequence was not isolated!")
        return False
    logger.info(f"Workflow profile: {workflows[0]}")
    logger.info("Sequence transition mapping: [PASS]")

    # 3. Suggestions generation and Interruption Policy
    logger.info("Testing suggestions matching and CPU/Presentation mode suppressions...")
    # Normal state
    normal_ctx = {"is_fullscreen": False, "in_meeting": False, "cpu_load": 15.0}
    sugs = engine.run_audit_cycle(normal_ctx)
    logger.info(f"Generated suggestions size: {len(sugs)}")
    if not sugs or sugs[0]["category"] != "workspace_prepare":
        logger.error("Workspace launch suggestions were not generated!")
        return False
    logger.info(f"Top Suggestion description:\n{sugs[0]['description']}")

    # Suppressed state (High CPU)
    high_cpu_ctx = {"is_fullscreen": False, "in_meeting": False, "cpu_load": 92.5}
    sugs_suppressed = engine.run_audit_cycle(high_cpu_ctx)
    logger.info(f"Suggestions count during High CPU load: {len(sugs_suppressed)}")
    if len(sugs_suppressed) != 0:
        logger.error("Interruption policy failed to suppress suggestion during high CPU states!")
        return False
    logger.info("Interruption policy block checking: [PASS]")

    # 4. Learning loop adjustments
    logger.info("Testing confidence adjustments per user feedback logs...")
    category = "workspace_prepare"
    initial_score = sugs[0]["confidence_score"]
    logger.info(f"Initial confidence score for [{category}]: {initial_score:.2f}")

    # Simulate REJECT clicks
    engine.record_suggestion_feedback(sugs[0]["id"], "REJECT")
    
    # Calculate score again
    sugs_decayed = engine.run_audit_cycle(normal_ctx)
    decayed_score = sugs_decayed[0]["confidence_score"] if sugs_decayed else 0.0
    logger.info(f"Decayed confidence score after REJECT feedback: {decayed_score:.2f}")
    if decayed_score >= initial_score:
        logger.error("Dismissed suggestions failed to decay confidence multipliers!")
        return False
    logger.info("Adaptive feedback loops calibrator: [PASS]")

    logger.info("Proactive Intelligence Engine Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_proactive_intelligence()
    sys.exit(0 if success else 1)
