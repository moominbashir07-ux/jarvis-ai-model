import os
import sys
import logging
from jarvis.core.logger import setup_logger
from jarvis.cognition.cognitive_database import CognitiveDatabase
from jarvis.cognition.goal_manager import GoalManager
from jarvis.cognition.task_decomposer import TaskDecomposer
from jarvis.cognition.objective_tracker import ObjectiveTracker
from jarvis.cognition.planner import PlanningEngine
from jarvis.cognition.strategy_selector import StrategySelector
from jarvis.cognition.hypothesis_engine import HypothesisEngine
from jarvis.cognition.confidence_engine import ConfidenceEngine
from jarvis.cognition.reflection_engine import ReflectionEngine
from jarvis.cognition.verifier import Verifier
from jarvis.cognition.uncertainty_estimator import UncertaintyEstimator
from jarvis.cognition.causal_reasoner import CausalReasoner
from jarvis.cognition.memory_retriever import MemoryRetriever
from jarvis.cognition.context_integrator import ContextIntegrator
from jarvis.cognition.cognition_manager import CognitionManager

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestCognition")

def test_cognition_pipeline():
    logger.info("==========================================")
    logger.info("       Cognition Core (Phase 20) Test     ")
    logger.info("==========================================")

    db_path = "logs/test_cognition_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # Setup CognitionManager coordinator facade
    manager = CognitionManager(db_path=db_path)

    # 1. Task Decomposer & Goal Manager
    logger.info("Testing task decomposer & goal manager...")
    subtasks = manager.decomposer.decompose_objective("Build a website")
    logger.info(f"Decomposed subtasks: {subtasks}")
    if len(subtasks) != 5:
        logger.error("TaskDecomposer failed to decompose objective correctly!")
        return False
    logger.info("Task Decomposer & Goal: [PASS]")

    # 2. Planning Engine & Strategy Selector
    logger.info("Testing planning engine and strategy selector...")
    plan = manager.planner.build_execution_plan(subtasks)
    logger.info(f"Execution plan: {plan}")
    if plan["overall_complexity"] != "MEDIUM" or plan["estimated_duration_mins"] != 25:
        logger.error("PlanningEngine returned incorrect plan calculations!")
        return False
        
    strategy = manager.strategy.select_execution_strategy(plan["overall_complexity"], network_online=True)
    logger.info(f"Selected strategy: {strategy}")
    if strategy != "distributed_cluster":
        logger.error("StrategySelector selected incorrect execution pathway!")
        return False
    logger.info("Planner & Strategy Selection: [PASS]")

    # 3. Hypothesis Engine ranking
    logger.info("Testing hypothesis ranking filters...")
    strong_hypotheses = manager.hypothesis.generate_and_rank_hypotheses("Find missing code block")
    logger.info(f"Strong hypotheses: {strong_hypotheses}")
    if len(strong_hypotheses) != 2:
        logger.error("HypothesisEngine failed to discard low confidence candidates!")
        return False
    logger.info("Hypothesis Engine: [PASS]")

    # 4. Confidence Engine calculations
    logger.info("Testing confidence score estimators...")
    conf = manager.confidence.estimate_confidence(10, 1)
    logger.info(f"Estimated confidence: {conf}")
    if conf != 0.91:
        logger.error("ConfidenceEngine returned incorrect probability value!")
        return False
    logger.info("Confidence Estimator: [PASS]")

    # 5. Reflection Engine logs
    logger.info("Testing reflection loop insight generation...")
    reflection = manager.reflection.evaluate_task_execution("Build a website", success=True)
    logger.info(f"Reflection insight: '{reflection}'")
    if "completed successfully" not in reflection:
        logger.error("ReflectionEngine failed to evaluate task execution!")
        return False
    logger.info("Reflection Loop: [PASS]")

    # 6. Verifier matches assertions
    logger.info("Testing completion verifier assertions...")
    ver_ok = manager.verifier.verify_action_result("Success", "SUCCESS")
    if not ver_ok:
        logger.error("Verifier failed to match case-insensitive text status!")
        return False
    logger.info("Verifier assertions: [PASS]")

    # 7. Uncertainty Estimator category
    logger.info("Testing uncertainty range classification...")
    cert_status = manager.uncertainty.estimate_uncertainty(6, 0)
    logger.info(f"Certainty level: {cert_status}")
    if cert_status != "highly_certain":
        logger.error("UncertaintyEstimator failed to flag high certainty bounds!")
        return False
    logger.info("Uncertainty bounds: [PASS]")

    # 8. Causal Reasoner dependency logging
    logger.info("Testing causal chain reasoning logs...")
    manager.causal.log_cause_and_effect("Goal Decompose", "Plan Formulated")
    logger.info(f"Causal chain list: {manager.causal.causal_chain}")
    if not manager.causal.causal_chain or "caused" not in manager.causal.causal_chain[0]:
        logger.error("CausalReasoner failed to append cause and effect event!")
        return False
    logger.info("Causal Reasoning: [PASS]")

    # 9. Memory Retriever contextual filtering
    logger.info("Testing memory retriever context filters...")
    relevant = manager.memory.retrieve_relevant_memories("personalization", ["user_profile", "personalization_metrics", "voice_settings"])
    logger.info(f"Retrieved memories: {relevant}")
    if len(relevant) != 1 or relevant[0] != "personalization_metrics":
        logger.error("MemoryRetriever failed to filter memories contextual lists!")
        return False
    logger.info("Memory Retriever: [PASS]")

    # 10. Context Integrator modality unifying
    logger.info("Testing multimodal context integration...")
    integrated = manager.context.integrate_contexts(
        voice={"text": "Open browser"},
        vision={"coordinates": [100, 200]},
        desktop={"active_app": "Chrome"}
    )
    logger.info(f"Integrated context: {integrated}")
    if integrated["integrated_desktop_active_app"] != "Chrome":
        logger.error("ContextIntegrator failed to map active app states!")
        return False
    logger.info("Context Integration: [PASS]")

    # 11. Cognition Manager E2E cycles runs
    logger.info("Testing CognitionManager E2E execution cycles...")
    cycle_res = manager.run_cognition_cycle("Build a website")
    logger.info(f"E2E Cognition results: {cycle_res}")
    if cycle_res["confidence_score"] != 0.91 or cycle_res["subtasks_count"] != 5:
        logger.error("CognitionManager E2E cycle outputs mismatch!")
        return False
    logger.info("Cognition Manager E2E: [PASS]")

    # Cleanup DB
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Cognitive Intelligence Core (Phase 20) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_cognition_pipeline()
    sys.exit(0 if success else 1)
