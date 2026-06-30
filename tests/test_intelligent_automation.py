import os
import sys
import time
import logging
from jarvis.core.logger import setup_logger
from jarvis.automation.intelligent.task_planner import TaskPlanner
from jarvis.automation.intelligent.action_generator import ActionGenerator
from jarvis.automation.intelligent.executor import IntelligentExecutor
from jarvis.automation.intelligent.recovery_engine import RecoveryEngine
from jarvis.automation.intelligent.workflow_builder import WorkflowBuilder

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestIntelligentAutomation")

def test_intelligent_automation_pipeline():
    logger.info("==========================================")
    logger.info("  Intelligent Automation (Phase E) Test   ")
    logger.info("==========================================")

    # Setup database helper
    db_path = "logs/test_automation_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    planner = TaskPlanner()
    generator = ActionGenerator()
    executor = IntelligentExecutor()
    recovery = RecoveryEngine()
    builder = WorkflowBuilder(db_path=db_path)

    # 1. Natural Language Task Planning
    goal = "Create PowerPoint presentation"
    logger.info(f"Planning task: {goal}")
    plan = planner.generate_plan(goal)
    logger.info(f"Execution graph generated with {len(plan['subtasks'])} actions.")
    if len(plan["subtasks"]) != 6:
        logger.error("Planning failed to generate correct subtask count!")
        return False

    # 2. Action Generation
    logger.info("Testing action generator properties...")
    actions = [generator.create_action(t) for t in plan["subtasks"]]
    if not actions or actions[0]["type"] != "LAUNCH_APP" or actions[0]["target"] != "PowerPoint":
        logger.error("Action generator fields mismatch!")
        return False
    for act in actions:
        for key in ("id", "type", "confidence", "target", "reason", "expected_result"):
            if key not in act:
                logger.error(f"Missing key in generated action: {key}")
                return False
    logger.info("Action details parsing: [PASS]")

    # 3. Intelligent Executor & Target Resolution
    logger.info("Testing semantic control resolution and execution...")
    # Executing launch app PowerPoint
    res1 = executor.execute_action(actions[0])
    logger.info(f"Launch App result success: {res1['success']}")
    if not res1["success"]:
        logger.error("Launch app step failed!")
        return False

    # Executing Click control 'Blank Presentation' (mock accessibility control target exists)
    res2 = executor.execute_action(actions[1])
    logger.info(f"Click control 'Blank Presentation' result success: {res2['success']}")
    if not res2["success"]:
        logger.error("Click control step failed!")
        return False
    logger.info("Target resolution: [PASS]")

    # 4. Recovery Engine
    logger.info("Testing popup detection and recovery shortcut strings...")
    # Simulate a dialog window popup list
    mock_popups = [{"hwnd": 99, "title": "Save changes dialog", "class_name": "#32770"}]
    blocker = recovery.check_modal_blockers(mock_popups)
    logger.info(f"Blocker detected: {blocker}")
    if not blocker or blocker["hwnd"] != 99:
        logger.error("Recovery failed to identify popup windows dialog!")
        return False
        
    # Test shortcut mapping for Click 'Save' failure
    failed_action = {"id": "t6", "type": "CLICK_CONTROL", "target": "Save"}
    rec_action = recovery.get_recovery_action(failed_action)
    logger.info(f"Formulated Recovery Action: {rec_action}")
    if rec_action["type"] != "SHORTCUT" or rec_action["target"] != "Ctrl+Shift+S":
        logger.error("Recovery shortcut mapper returned incorrect hotkey!")
        return False
    logger.info("Popup recovery: [PASS]")

    # 5. Workflow Builder Database serialization
    logger.info("Testing workflow macros saving and database restores...")
    steps = [
        {"action": "LAUNCH_APP", "target": "Code.exe"},
        {"action": "LAUNCH_APP", "target": "Terminal.exe"}
    ]
    builder.save_workflow("Development Workspace", steps, success_rate=0.98, duration=4.5)
    
    loaded = builder.get_workflow("Development Workspace")
    logger.info(f"Loaded workflow: {loaded}")
    if not loaded or len(loaded["steps"]) != 2 or loaded["steps"][0]["target"] != "Code.exe":
        logger.error("Workspace workflow restoration from SQLite failed!")
        return False
    logger.info("Workflow database logs: [PASS]")

    # Cleanup DB
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Intelligent Automation (Phase E) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_intelligent_automation_pipeline()
    sys.exit(0 if success else 1)
