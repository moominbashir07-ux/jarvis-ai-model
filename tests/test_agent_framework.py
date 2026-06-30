import os
import time
import logging
from pathlib import Path
from jarvis.core.logger import setup_logger
from jarvis.agents.registry import agent_registry
from jarvis.agents.planner_agent import PlannerAgent
from jarvis.agents.memory_agent import MemoryAgent
from jarvis.agents.automation_agent import AutomationAgent
from jarvis.agents.vision_agent import VisionAgent
from jarvis.agents.conversation_agent import ConversationAgent
from jarvis.agents.supervisor_agent import SupervisorAgent
from jarvis.agents.research_agent import ResearchAgent
from jarvis.agents.orchestrator import CoreOrchestrator

# Setup basic logging to console
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestAgentFramework")

def test_agent_framework_lifecycle():
    logger.info("--- Starting Autonomous Agent Framework Verification ---")
    
    # 1. Clear and register cooperating agents in global AgentRegistry
    agent_registry.clear()
    
    planner = PlannerAgent()
    memory_agent = MemoryAgent()
    automation_agent = AutomationAgent()
    vision_agent = VisionAgent()
    conv_agent = ConversationAgent()
    supervisor = SupervisorAgent()
    research_agent = ResearchAgent()
    orchestrator = CoreOrchestrator()
    
    agent_registry.register_agent(planner)
    agent_registry.register_agent(memory_agent)
    agent_registry.register_agent(automation_agent)
    agent_registry.register_agent(vision_agent)
    agent_registry.register_agent(conv_agent)
    agent_registry.register_agent(supervisor)
    agent_registry.register_agent(research_agent)
    agent_registry.register_agent(orchestrator)
    
    # Clean output files
    brief_path = "logs/ai_chips_brief.txt"
    if os.path.exists(brief_path):
        os.remove(brief_path)

    # 2. Run multi-step research and summary creation goal
    goal = "Research the latest AI chips and summarize them into a document."
    logger.info(f"Submitting high-level goal: '{goal}'")
    
    start_time = time.time()
    result = orchestrator.run(goal)
    duration = time.time() - start_time
    
    logger.info(f"Execution Completed in {duration:.4f}s. Success status: {result['success']}")
    if not result["success"]:
        logger.error(f"Orchestrator failed: {result.get('error')}")
        return False

    # 3. Validate context outputs
    completed = result["completed_tasks"]
    logger.info(f"Completed Tasks in Graph: {completed}")
    
    if "research_chips" not in completed or "write_summary" not in completed or "locate_save" not in completed:
        logger.error("Not all dependency tasks were completed!")
        return False
        
    # Validate the written summary brief file
    logger.info(f"Verifying target output summary file: '{brief_path}'")
    if not os.path.exists(brief_path):
        logger.error("Research summary file was not created!")
        return False
        
    brief_content = Path(brief_path).read_text(encoding='utf-8')
    logger.info(f"Written File Content snippet:\n{brief_content}")

    # 4. Validate Vision Agent location mapping coordinate center math
    vision_res = result["results"]["locate_save"]
    logger.info(f"Vision coordinate result: {vision_res}")
    if not vision_res["found"] or vision_res["x"] != 475 or vision_res["y"] != 312:
        logger.error("Vision Agent failed to return correct target coordinates!")
        return False

    # 5. Clean up output files
    if os.path.exists(brief_path):
        os.remove(brief_path)

    logger.info("Autonomous Agent Framework Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS Agent Framework Integration Tests")
    logger.info("==========================================")
    
    test_agent_framework_lifecycle()
