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
from jarvis.agents.planner_agent import PlannerAgent
from jarvis.agents.memory_agent import MemoryAgent
from jarvis.agents.automation_agent import AutomationAgent
from jarvis.agents.vision_agent import VisionAgent
from jarvis.agents.conversation_agent import ConversationAgent
from jarvis.agents.supervisor_agent import SupervisorAgent
from jarvis.agents.research_agent import ResearchAgent
from jarvis.agents.orchestrator import CoreOrchestrator
from package_jarvis import package_app

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestCertification")

def test_full_certification() -> bool:
    logger.info("==================================================")
    logger.info("  JARVIS AI OS - V1.0 PRODUCTION CERTIFICATION  ")
    logger.info("==================================================")

    logger.info("--- 1. Voice Certification checks ---")
    health = HealthManager()
    status = health.get_status_report()
    logger.info(f"Microphone Status: {status['devices']['microphone']}")
    logger.info(f"Speaker Status: {status['devices']['speaker']}")
    if status['devices']['microphone'] != "ONLINE" or status['devices']['speaker'] != "ONLINE":
        logger.error("Audio hardware interface error detected!")
        return False
    logger.info("Voice status: [PASS]")

    logger.info("--- 2. Provider Failover and Circuit Breaker Certification ---")
    from jarvis.brain.router import ProviderRouter
    router = ProviderRouter()
    router.circuits["openai"].record_failure()
    router.circuits["openai"].record_failure()
    router.circuits["gemini"].record_failure()
    router.circuits["gemini"].record_failure()
    
    logger.info(f"OpenAI Breaker Status: {router.circuits['openai'].state}")
    logger.info(f"Gemini Breaker Status: {router.circuits['gemini'].state}")
    
    primary, fallback = router.select_model("Write python code to parse logs.")
    logger.info(f"Selected Failover Model for Task [coding]: primary={primary}, fallback={fallback}")
    if primary != "local":
        logger.error("Failover routing did not bypass tripped breakers!")
        return False
    logger.info("Provider failover checks: [PASS]")

    logger.info("--- 3. Workspace Automation Certification ---")
    from jarvis.automation.sys_control import SystemController
    sys_control = SystemController()
    sys_control.allow_unsafe = True
    
    sys_control.write_clipboard("Certification Token")
    success, clip_text = sys_control.read_clipboard()
    logger.info(f"Clipboard verification success={success}: '{clip_text}'")
    if not success or clip_text != "Certification Token":
        logger.error("System clipboard write/read context mismatch!")
        return False
    logger.info("Workspace automation checks: [PASS]")

    logger.info("--- 4. Visual Bounding Box & Cache Certification ---")
    from jarvis.vision.vision_manager import VisionManager
    vision = VisionManager()
    vision.enabled = True
    
    found, cx, cy = vision.locate_text_on_screen("Save")
    logger.info(f"Coordinate Locating verification for 'Save': {found} -> ({cx}, {cy})")
    if not found or cx != 475 or cy != 312:
        logger.error("Vision Agent coordinate locator math error!")
        return False
    logger.info("Visual coordinates and caches checks: [PASS]")

    logger.info("--- 5. Research Caching & Claim Contradiction Certification ---")
    agent = ResearchAgent()
    agent.initialize()
    
    query = "nuclear fusion net energy gain"
    try:
        agent.cache.db.execute("DELETE FROM research_cache WHERE query = ?", (query.strip().lower(),))
        agent.cache.db.commit()
    except Exception:
        pass

    r1 = agent.run(query)
    logger.info(f"Initial research task cache hit status: {r1.get('cache_hit')} (Expected: False)")
    if r1.get("cache_hit") is True:
        logger.error("First cache check returned positive hit!")
        return False

    r2 = agent.run(query)
    logger.info(f"Second research task cache hit status: {r2.get('cache_hit')} (Expected: True)")
    if r2.get("cache_hit") is not True:
        logger.error("Second cache check missed stored report!")
        return False

    logger.info("Verifying science domain reputation scoring and contradictory claims...")
    claims = r2.get("report", {}).get("conflicting_evidence", [])
    logger.info(f"Timeline Contradictions parsed: {len(claims)}")
    if len(claims) != 2:
        logger.error("Research engine failed to parse timeline claims!")
        return False
    logger.info("Research caching and claim check checks: [PASS]")

    logger.info("--- 6. Autonomous Cooperating Agent Framework Certification ---")
    agent_registry.clear()
    
    planner = PlannerAgent()
    memory_agent = MemoryAgent()
    automation_agent = AutomationAgent()
    vision_agent = VisionAgent()
    conv_agent = ConversationAgent()
    supervisor = SupervisorAgent()
    orchestrator = CoreOrchestrator()
    
    agent_registry.register_agent(planner)
    agent_registry.register_agent(memory_agent)
    agent_registry.register_agent(automation_agent)
    agent_registry.register_agent(vision_agent)
    agent_registry.register_agent(conv_agent)
    agent_registry.register_agent(supervisor)
    agent_registry.register_agent(agent)
    agent_registry.register_agent(orchestrator)

    goal = "Research the latest AI chips and summarize them into a document."
    logger.info(f"Orchestrator goal execution: '{goal}'")
    
    brief_path = "logs/ai_chips_brief.txt"
    if os.path.exists(brief_path):
        os.remove(brief_path)

    res = orchestrator.run(goal)
    logger.info(f"Orchestrator execution status success: {res['success']}")
    if not res["success"] or not os.path.exists(brief_path):
        logger.error("Multi-agent orchestrator execution graph aborted!")
        return False

    brief_content = Path(brief_path).read_text(encoding='utf-8')
    logger.info(f"Written Brief File snippet:\n{brief_content}")
    if "Title:" not in brief_content:
        logger.error("Written document template schema corrupt!")
        return False

    if os.path.exists(brief_path):
        os.remove(brief_path)
    logger.info("Cooperating Agent Framework checks: [PASS]")

    logger.info("--- 7. Watchdog, Updater & Packaging Certification ---")
    build_success = package_app()
    if not build_success:
        logger.error("Installer config check failed!")
        return False

    updater = AutoUpdater(current_version="1.0.0")
    fail_payload = {"latest_version": "1.0.1", "simulate_fail": True}
    updater_success, msg = updater.apply_update(fail_payload)
    logger.info(f"Auto Updater rollback check: {updater_success} ({msg})")
    if not updater_success or "Rollback complete" not in msg:
        logger.error("Updater rollback recovery failed!")
        return False

    watchdog = ProcessWatchdog()
    recovered = watchdog.recover_subsystem("backend_thread")
    logger.info(f"Watchdog exception recovery reset: {recovered}")
    if not recovered:
        logger.error("Watchdog reset failed!")
        return False
    watchdog.shutdown()
    logger.info("Watchdog, Updater & Packaging checks: [PASS]")

    logger.info("\n==================================================")
    logger.info("  JARVIS AI OS PRODUCTION CERTIFICATION SUCCESS!  ")
    logger.info("==================================================")
    return True

if __name__ == "__main__":
    success = test_full_certification()
    sys.exit(0 if success else 1)
