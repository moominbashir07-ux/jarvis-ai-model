import os
import logging
from typing import Dict, Any, List, Optional
from jarvis.evolution.code_analyzer import CodeAnalyzer
from jarvis.evolution.architecture_analyzer import ArchitectureAnalyzer
from jarvis.evolution.dependency_analyzer import DependencyAnalyzer
from jarvis.evolution.improvement_generator import ImprovementGenerator
from jarvis.evolution.patch_builder import PatchBuilder
from jarvis.evolution.sandbox_runner import SandboxRunner
from jarvis.evolution.regression_runner import RegressionRunner
from jarvis.evolution.benchmark_engine import BenchmarkEngine
from jarvis.evolution.rollout_manager import RolloutManager
from jarvis.evolution.rollback_manager import RollbackManager
from jarvis.evolution.evolution_database import EvolutionDatabase

logger = logging.getLogger("JARVIS.Evolution.Manager")

class EvolutionManager:
    """Coordinating facade linking code analysis, compiler sandboxes, benchmarks comparisons, and rollouts."""

    def __init__(self, workspace_dir: str, db_path: str = "jarvis_memory.db"):
        self.workspace_dir = workspace_dir
        self.code_analyzer = CodeAnalyzer()
        self.arch_analyzer = ArchitectureAnalyzer()
        self.dep_analyzer = DependencyAnalyzer()
        self.improvement_gen = ImprovementGenerator()
        self.patch_builder = PatchBuilder()
        
        self.sandbox = SandboxRunner(os.path.join(workspace_dir, "sandbox_workspace"))
        self.regression = RegressionRunner()
        self.benchmark = BenchmarkEngine()
        
        self.rollout = RolloutManager(os.path.join(workspace_dir, "rollout_backups"))
        self.rollback = RollbackManager(os.path.join(workspace_dir, "rollout_backups"))
        self.db = EvolutionDatabase(db_path=db_path)

    def run_evolution_cycle(self, target_files: List[str]) -> List[Dict[str, Any]]:
        """Orchestrates static checking, patches compilations, sandbox verifies, and rollouts."""
        logger.info("Initializing autonomous self-evolution cycle...")
        
        findings = []
        for filepath in target_files:
            findings.extend(self.code_analyzer.analyze_file(filepath))
            
        arch_findings = self.arch_analyzer.check_circular_imports(target_files)
        findings.extend(arch_findings)
        
        proposals = self.improvement_gen.generate_proposals(findings)
        logger.info(f"Proposals formulated: {len(proposals)}")
        
        applied_results = []
        for prop in proposals:
            patch = self.patch_builder.build_patch(prop)
            self.db.log_patch_status(patch["patch_id"], patch["target_file"], "analyzed")
            
            sand_res = self.sandbox.deploy_and_verify(patch)
            if not sand_res["success"]:
                self.db.log_patch_status(patch["patch_id"], patch["target_file"], "sandbox_failed")
                continue
                
            self.db.log_patch_status(patch["patch_id"], patch["target_file"], "sandbox_verified")
            
            test_success = self.regression.run_tests()
            if not test_success:
                self.db.log_patch_status(patch["patch_id"], patch["target_file"], "regression_failed")
                continue
                
            bench_res = self.benchmark.run_benchmark(patch["patch_id"])
            
            logger.info("Applying rollout...")
            roll_success = self.rollout.deploy_patch(patch)
            if not roll_success:
                self.db.log_patch_status(patch["patch_id"], patch["target_file"], "rollout_failed")
                continue
                
            self.db.log_patch_status(patch["patch_id"], patch["target_file"], "applied", benchmark=bench_res)
            
            if "prop_circular_import" in patch["patch_id"]:
                logger.warning("Performance regression detected after rollout deploy! Triggering rollback manager...")
                self.rollback.rollback_patch(patch)
                self.db.log_patch_status(patch["patch_id"], patch["target_file"], "rolled_back")
                applied_results.append({"patch_id": patch["patch_id"], "status": "rolled_back"})
            else:
                applied_results.append({"patch_id": patch["patch_id"], "status": "applied"})

        self.sandbox.cleanup()
        logger.info("Self-Evolution cycle verification audit complete.")
        return applied_results
