import os
import sys
import shutil
import logging
from jarvis.core.logger import setup_logger
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
from jarvis.evolution.evolution_scheduler import EvolutionScheduler
from jarvis.evolution.evolution_manager import EvolutionManager

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestSelfEvolution")

def test_self_evolution_pipeline():
    logger.info("==========================================")
    logger.info("      Self-Evolution (Phase 17) Test      ")
    logger.info("==========================================")

    # Setup sandbox workspace paths
    workspace_dir = "logs/test_evolution_workspace"
    db_path = "logs/test_evolution_memory.db"
    dummy_code_file = "logs/test_evolution_target.py"
    circular_file_a = "logs/test_circ_a.py"
    circular_file_b = "logs/test_circ_b.py"

    # Purge existing
    for path in (workspace_dir, dummy_code_file, circular_file_a, circular_file_b):
        if os.path.exists(path):
            try:
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
            except Exception:
                pass
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    # Create target code file missing type hints and docstring
    dummy_code = """
def execute_analysis():
    print("Self Analysis Run")
"""
    os.makedirs(os.path.dirname(dummy_code_file), exist_ok=True)
    with open(dummy_code_file, "w", encoding="utf-8") as f:
        f.write(dummy_code)

    # Create circular import pair
    with open(circular_file_a, "w", encoding="utf-8") as f:
        f.write("import test_circ_b\n")
    with open(circular_file_b, "w", encoding="utf-8") as f:
        f.write("import test_circ_a\n")

    # 1. AST Code Analyzer
    logger.info("Testing code AST parser checks...")
    code_an = CodeAnalyzer()
    findings = code_an.analyze_file(dummy_code_file)
    logger.info(f"Code parser findings: {findings}")
    if len(findings) != 2:
        logger.error("CodeAnalyzer failed to identify missing annotations or docstrings!")
        return False
    logger.info("AST Code Analyzer: [PASS]")

    # 2. Architecture Analyzer
    logger.info("Testing circular imports coupling check...")
    arch_an = ArchitectureAnalyzer()
    arch_findings = arch_an.check_circular_imports([circular_file_a, circular_file_b])
    logger.info(f"Circular import findings: {arch_findings}")
    if not arch_findings or arch_findings[0]["type"] != "circular_import":
        logger.error("ArchitectureAnalyzer failed to identify circular imports loops!")
        return False
    logger.info("Architecture coupling check: [PASS]")

    # 3. Dependency Analyzer
    logger.info("Testing dependency audit scanner...")
    dep_an = DependencyAnalyzer()
    deps = dep_an.check_outdated_packages()
    logger.info(f"Outdated packages list: {deps}")
    if not deps or deps[0]["package"] != "websockets":
        logger.error("Dependency analyzer package lookup failed!")
        return False
    logger.info("Dependency audits: [PASS]")

    # 4. Improvement Generator & Patch Builder
    logger.info("Testing patch formulation and rollback metadata builders...")
    gen = ImprovementGenerator()
    builder = PatchBuilder()
    
    # Merge findings to generate proposals
    all_findings = findings + arch_findings
    proposals = gen.generate_proposals(all_findings)
    logger.info(f"Proposals list: {proposals}")
    if len(proposals) != 2:
        logger.error("Improvement proposal count mismatch!")
        return False
        
    patch = builder.build_patch(proposals[0])
    logger.info(f"Assembled Patch Bundle: {patch}")
    for key in ("patch_id", "target_file", "original_content", "replacement_content", "rollback_info"):
        if key not in patch:
            logger.error(f"Missing key in patch bundle parameters: {key}")
            return False
    logger.info("Patch compilations: [PASS]")

    # 5. Sandbox Runner
    logger.info("Testing sandbox verification checks...")
    sandbox = SandboxRunner(os.path.join(workspace_dir, "sandbox"))
    sand_res = sandbox.deploy_and_verify(patch)
    logger.info(f"Sandbox verify result: {sand_res}")
    if not sand_res["success"] or not os.path.exists(sand_res["sandbox_path"]):
        logger.error("Sandbox deployment verify check failed!")
        return False
    sandbox.cleanup()
    logger.info("Sandbox verification: [PASS]")

    # 6. Benchmark Engine
    logger.info("Testing benchmark performance comparison stats...")
    bench = BenchmarkEngine()
    metrics = bench.run_benchmark(patch["patch_id"])
    logger.info(f"Benchmark metrics output: {metrics}")
    if metrics["performance_increase_percent"] != 9.6:
        logger.error("Benchmark performance gain comparison stats mismatch!")
        return False
    logger.info("Benchmark comparer: [PASS]")

    # 7. Rollout Manager & Rollback manager loops
    logger.info("Testing rollout updates and fallback rollbacks on failure...")
    # Setup Manager orchestrator
    manager = EvolutionManager(workspace_dir=workspace_dir, db_path=db_path)
    
    # Run the cycle to verify rollout & rollback
    target_files = [dummy_code_file, circular_file_a, circular_file_b]
    results = manager.run_evolution_cycle(target_files)
    logger.info(f"Evolution manager cycle results: {results}")
    
    # Prop Circular Import should trigger a fallback rollback
    rolled_back_prop = next((r for r in results if r["status"] == "rolled_back"), None)
    if not rolled_back_prop:
        logger.error("EvolutionManager failed to trigger rollback loop on performance regression!")
        return False
        
    # Verify original target content remains correct
    with open(circular_file_a, "r", encoding="utf-8") as f:
        original_circ = f.read()
    logger.info(f"Circ A contents after rollback: '{original_circ.strip()}'")
    if "import test_circ_b" not in original_circ:
        logger.error("Rollback failed to restore circular file backup contents!")
        return False
    logger.info("Rollout & Rollback loops: [PASS]")

    # 8. Evolution Scheduler
    logger.info("Testing scheduler trigger timers...")
    triggered = False
    def scheduler_cb():
        nonlocal triggered
        triggered = True
        
    sched = EvolutionScheduler(scheduler_cb)
    sched.trigger_now()
    if not triggered:
        logger.error("Evolution scheduler callback failed to trigger!")
        return False
    logger.info("Scheduler triggers: [PASS]")

    # Cleanup temp
    for path in (workspace_dir, dummy_code_file, circular_file_a, circular_file_b):
        if os.path.exists(path):
            try:
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
            except Exception:
                pass
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    logger.info("Self-Evolution (Phase 17) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_self_evolution_pipeline()
    sys.exit(0 if success else 1)
