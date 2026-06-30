import os
import sys
import time
import logging
from jarvis.core.logger import setup_logger
from jarvis.agents.dynamic.agent_registry import DynamicAgentRegistry
from jarvis.agents.dynamic.agent_factory import AgentFactory
from jarvis.agents.dynamic.task_marketplace import TaskMarketplace
from jarvis.agents.dynamic.collaboration_engine import CollaborationEngine
from jarvis.agents.dynamic.communication_bus import AgentCommunicationBus
from jarvis.agents.dynamic.agent_optimizer import AgentOptimizer
from jarvis.agents.dynamic.failure_coordinator import FailureCoordinator
from jarvis.agents.dynamic.collective_memory import CollectiveMemory
from jarvis.agents.dynamic.scheduler import MultiAgentScheduler

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestMultiAgentExpansion")

def test_multi_agent_expansion_pipeline():
    logger.info("==========================================")
    logger.info("  Multi-Agent Expansion (Phase F) Test    ")
    logger.info("==========================================")

    # Setup database paths
    db_path = "logs/test_agent_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    registry = DynamicAgentRegistry(db_path=db_path)
    factory = AgentFactory()
    marketplace = TaskMarketplace()
    collab = CollaborationEngine(marketplace)
    bus = AgentCommunicationBus()
    optimizer = AgentOptimizer()
    failure_coord = FailureCoordinator(marketplace)
    memory = CollectiveMemory(db_path=db_path)
    scheduler = MultiAgentScheduler()

    # 1. Dynamic Agent Catalog Registration
    logger.info("Testing dynamic agent registration...")
    registry.register_agent("CodingAgent_v2", "2.0.0", ["Coding", "Refactoring"])
    registry.register_agent("VisionAgent_v1", "1.0.0", ["OCR", "Locator"])
    
    enabled = registry.get_enabled_agents()
    logger.info(f"Active Registry catalog agents: {enabled}")
    if len(enabled) != 2 or enabled[0]["name"] != "CodingAgent_v2":
        logger.error("Registry failed to serialize dynamic agent catalog!")
        return False
        
    registry.disable_agent("VisionAgent_v1")
    enabled_after = registry.get_enabled_agents()
    if len(enabled_after) != 1:
        logger.error("Deactivating agent failed!")
        return False
    logger.info("Agent Catalog Registry: [PASS]")

    # 2. Agent Factory Instantiation
    logger.info("Testing agent instantiation factory...")
    c_agent = factory.create_agent("CodingAgent", ["Coding", "Refactoring"])
    v_agent = factory.create_agent("VisionAgent", ["OCR", "Locator"])
    
    if c_agent.name != "CodingAgent" or "OCR" not in v_agent.capabilities:
        logger.error("Agent factory instantiation property mismatch!")
        return False
    logger.info("Agent Factory Clones: [PASS]")

    # 3. Collaboration Engine & Marketplace routing
    logger.info("Testing marketplace registration and collaboration routing...")
    marketplace.join_marketplace(c_agent)
    marketplace.join_marketplace(v_agent)
    
    subtasks = [
        {"id": "st1", "requirement": "Refactoring coding logic", "goal": "Optimize loop"},
        {"id": "st2", "requirement": "OCR bounds coordinate", "goal": "Find element"}
    ]
    res = collab.execute_goal("Compile code and click bounds", subtasks)
    logger.info(f"Collaboration execution result: {res}")
    if not res["success"] or len(res["subtasks_results"]) != 2:
        logger.error("Collaboration parallel dispatch execution graph failed!")
        return False
    logger.info("Collaboration & Marketplace routing: [PASS]")

    # 4. Agent Communication Bus
    logger.info("Testing thread-safe communication event bus...")
    received_payload = {}
    def on_bus_msg(payload):
        nonlocal received_payload
        received_payload = payload
        
    bus.subscribe("AgentAlert", on_bus_msg)
    bus.publish("AgentAlert", {"message": "Critical process error"})
    logger.info(f"Received bus notification frame: {received_payload}")
    if received_payload.get("message") != "Critical process error":
        logger.error("Communication bus pub/sub message delivery failed!")
        return False
    logger.info("Communication Bus: [PASS]")

    # 5. Agent Optimizer
    logger.info("Testing latency performance audit optimizer...")
    c_agent.latency_history = [1.2, 1.5, 0.9] # Average: 1.2s > threshold (1.0s)
    v_agent.latency_history = [0.2, 0.3] # Average: 0.25s
    
    opts = optimizer.optimize_agent_pool([c_agent, v_agent])
    logger.info(f"Performance Optimization recommendations: {opts}")
    if not opts or opts[0]["agent_name"] != "CodingAgent":
        logger.error("Optimizer failed to identify bottleneck dynamic agents!")
        return False
    logger.info("Agent Optimizer: [PASS]")

    # 6. Failure Coordinator Timeout Re-routing
    logger.info("Testing timeout failure coordinator and cloning reassignments...")
    failed_task = {"id": "st3", "requirement": "OCR locator math", "goal": "Check target"}
    fail_res = failure_coord.handle_agent_timeout("VisionAgent", failed_task)
    logger.info(f"Timeout recovery result: {fail_res}")
    if not fail_res["success"] or "clone" not in fail_res["agent_name"]:
        logger.error("FailureCoordinator failed to reallocate timeout task to fallback dynamic clone!")
        return False
    logger.info("Failure Coordinator: [PASS]")

    # 7. Collective Memory SQLite Logs
    logger.info("Testing collective memory logs traces...")
    memory.post_message("Coding_Debate", "CodingAgent", {"opinion": "Use WAL sqlite mode"})
    messages = memory.get_messages("Coding_Debate")
    logger.info(f"Conversation traces logged: {messages}")
    if not messages or messages[0]["sender"] != "CodingAgent":
        logger.error("Dialogue message logs failed to persist in collective memory!")
        return False
    logger.info("Collective Memory logs: [PASS]")

    # 8. Priority Multi-Agent Scheduler
    logger.info("Testing priority scheduler queue popping order...")
    scheduler.schedule_task(priority=10, task={"id": "low_task"})
    scheduler.schedule_task(priority=1, task={"id": "high_task"})
    
    t_first = scheduler.pop_task()
    t_second = scheduler.pop_task()
    logger.info(f"First popped: {t_first} | Second: {t_second}")
    if t_first["id"] != "high_task" or t_second["id"] != "low_task":
        logger.error("Scheduler queue popped tasks in incorrect priority order!")
        return False
    logger.info("Priority Multi-Agent Scheduler: [PASS]")

    # Cleanup DB
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Multi-Agent Expansion (Phase F) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_multi_agent_expansion_pipeline()
    sys.exit(0 if success else 1)
