import logging
from typing import Dict, Any, List
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

logger = logging.getLogger("JARVIS.Cognition.Manager")

class CognitionManager:
    """Coordinating facade system linking planner decomposers, LWW conflict resolvers, and reflections."""

    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db = CognitiveDatabase(db_path=db_path)
        self.goal_mgr = GoalManager()
        self.decomposer = TaskDecomposer()
        self.tracker = ObjectiveTracker()
        
        self.planner = PlanningEngine()
        self.strategy = StrategySelector()
        self.hypothesis = HypothesisEngine()
        
        self.confidence = ConfidenceEngine()
        self.reflection = ReflectionEngine()
        self.verifier = Verifier()
        self.uncertainty = UncertaintyEstimator()
        
        self.causal = CausalReasoner()
        self.memory = MemoryRetriever()
        self.context = ContextIntegrator()

    def run_cognition_cycle(self, objective: str) -> Dict[str, Any]:
        """Orchestrates goal decompositions, hypothesis generations, confidence estimators, and reflections."""
        logger.info("Initializing cognitive intelligence reasoning pipeline...")
        
        subtasks = self.decomposer.decompose_objective(objective)
        goal_id = f"goal_{objective.lower().replace(' ', '_')}"
        self.goal_mgr.add_goal(goal_id, objective, status="active")
        
        plan = self.planner.build_execution_plan(subtasks)
        
        pathway = self.strategy.select_execution_strategy(plan["overall_complexity"], network_online=True)
        
        hypotheses = self.hypothesis.generate_and_rank_hypotheses(objective)
        
        conf = self.confidence.estimate_confidence(success_count=10, failure_count=1)
        self.db.log_goal(goal_id, objective, status="active", conf=conf)
        
        self.causal.log_cause_and_effect("CompileSandbox", "ExecutionSuccess")
        
        reflection_log = self.reflection.evaluate_task_execution(objective, success=True)
        self.db.log_reflection(goal_id, reflection_log, success=True)
        
        self.goal_mgr.update_goal_status(goal_id, status="completed")
        self.db.log_goal(goal_id, objective, status="completed", conf=conf)
        
        logger.info("Cognitive pipeline cycle finished successfully.")
        return {
            "goal_id": goal_id,
            "subtasks_count": len(subtasks),
            "selected_strategy": pathway,
            "confidence_score": conf,
            "reflection": reflection_log
        }
