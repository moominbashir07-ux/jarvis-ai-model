import os
import sys
import time
import logging
from jarvis.core.logger import setup_logger
from jarvis.personalization.db_helper import PersonalizationDB
from jarvis.personalization.profile_manager import UserProfileManager
from jarvis.personalization.habit_engine import HabitLearningEngine
from jarvis.personalization.preference_engine import PreferenceEngine
from jarvis.personalization.routine_detector import RoutineDetector
from jarvis.personalization.recommendation_engine import RecommendationEngine
from jarvis.personalization.goal_predictor import GoalPredictionEngine
from jarvis.personalization.workspace_memory import WorkspaceMemory
from jarvis.personalization.adaptive_scheduler import AdaptiveScheduler

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestPersonalization")

def test_personalization_subsystems():
    logger.info("==========================================")
    logger.info("  Adaptive Personalization Engine Test    ")
    logger.info("==========================================")

    # Use a separate test database to avoid polluting main state
    db_path = "logs/test_personalization_memory.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    db = PersonalizationDB(db_path=db_path)

    # 1. Database Schema & Backup checks
    logger.info("Testing SQLite backups and restores...")
    backup_path = "logs/test_personalization_backup.bak"
    if os.path.exists(backup_path):
        try:
            os.remove(backup_path)
        except Exception:
            pass
            
    success = db.create_backup(backup_path)
    if not success or not os.path.exists(backup_path):
        logger.error("Database backup creation failed!")
        return False
        
    success_restore = db.restore_backup(backup_path)
    if not success_restore:
        logger.error("Database restore from backup failed!")
        return False
    logger.info("DB Migrations and Backup: [PASS]")

    # 2. UserProfileManager
    logger.info("Testing User Profile manager preferences set/get...")
    profile = UserProfileManager(db)
    profile.set_preference("openai_model", "gpt-4o")
    profile.set_preference("favorite_ide", "VS Code")
    
    val = profile.get_preference("openai_model")
    logger.info(f"Retrieved Preference: {val}")
    if val != "gpt-4o":
        logger.error("Preference property fetch mismatch!")
        return False
        
    # Export/Import check
    export_str = profile.export_profile()
    logger.info(f"Exported Profile:\n{export_str}")
    
    profile.set_preference("openai_model", "gpt-3.5")
    profile.import_profile(export_str)
    val_restored = profile.get_preference("openai_model")
    if val_restored != "gpt-4o":
        logger.error("Profile import rollback restoration failed!")
        return False
    logger.info("UserProfileManager: [PASS]")

    # 3. HabitLearningEngine
    logger.info("Testing Habit engine tracking logs...")
    habits = HabitLearningEngine(db)
    habits.record_activity("Code.exe")
    habits.record_activity("Code.exe")
    habits.record_activity("Chrome.exe")
    
    freq = habits.get_habit_frequency("Code.exe")
    logger.info(f"Habit frequency count: {freq}")
    if freq != 2:
        logger.error("Habit record counter mismatch!")
        return False
        
    top_habits = habits.get_frequent_habits(limit=2)
    logger.info(f"Top Habits: {top_habits}")
    if len(top_habits) != 2 or top_habits[0]["habit_name"] != "code.exe":
        logger.error("Frequent habits sorting or keys missing!")
        return False
    logger.info("HabitLearningEngine: [PASS]")

    # 4. PreferenceEngine
    logger.info("Testing Preference scoring adjustments...")
    prefs = PreferenceEngine(db)
    initial_mult = prefs.get_multiplier("workspace_prepare")
    logger.info(f"Initial multiplier: {initial_mult:.2f}")
    
    prefs.log_feedback("sug_1", "workspace_prepare", "ACCEPT")
    accepted_mult = prefs.get_multiplier("workspace_prepare")
    logger.info(f"Accepted multiplier: {accepted_mult:.2f}")
    if accepted_mult <= initial_mult:
        logger.error("Multiplier failed to increment on ACCEPT feedback!")
        return False
        
    prefs.log_feedback("sug_1", "workspace_prepare", "REJECT")
    rejected_mult = prefs.get_multiplier("workspace_prepare")
    logger.info(f"Rejected multiplier: {rejected_mult:.2f}")
    if rejected_mult >= accepted_mult:
        logger.error("Multiplier failed to decay on REJECT feedback!")
        return False
    logger.info("PreferenceEngine: [PASS]")

    # 5. RoutineDetector
    logger.info("Testing Routine templates recording...")
    routines = RoutineDetector(db)
    routines.register_routine("Coding Setup", ["Code.exe", "Terminal.exe"], 0.95)
    
    list_routines = routines.get_detected_routines()
    logger.info(f"Detected routines: {list_routines}")
    if not list_routines or list_routines[0]["name"] != "Coding Setup":
        logger.error("Routine template load failure!")
        return False
    logger.info("RoutineDetector: [PASS]")

    # 6. RecommendationEngine
    logger.info("Testing Recommendation generator weighting...")
    recs = RecommendationEngine(db, prefs)
    results = recs.generate_recommendations("Code.exe", ["src/core.py", "research/paper.pdf"])
    logger.info(f"Recommendations count: {len(results)}")
    if not results or results[0]["category"] != "workspace_prepare":
        logger.error("Recommendation category scoring order is incorrect!")
        return False
    logger.info(f"Top Recommendation: {results[0]}")
    logger.info("RecommendationEngine: [PASS]")

    # 7. GoalPredictionEngine
    logger.info("Testing Goal sequence action predictor...")
    goals = GoalPredictionEngine(db)
    pred_results = goals.predict_goals(["Code.exe"])
    logger.info(f"Goal Predictions likelihood: {pred_results}")
    if not pred_results or pred_results[0]["action"] != "Launch Terminal":
        logger.error("Goal predictor output heuristic mismatch!")
        return False
    logger.info("GoalPredictionEngine: [PASS]")

    # 8. WorkspaceMemory
    logger.info("Testing Workspace layout saving and loading state...")
    memory = WorkspaceMemory(db)
    details = {"ide": "VS Code", "layout": "split", "active_files": ["main.py"]}
    memory.save_workspace_state("c:/projects/my_app", details)
    
    loaded = memory.load_workspace_state("c:/projects/my_app")
    logger.info(f"Loaded workspace state: {loaded}")
    if not loaded or loaded["layout"] != "split":
        logger.error("Workspace state serialization/load failed!")
        return False
    logger.info("WorkspaceMemory: [PASS]")

    # Cleanup DB test files
    db.close()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    if os.path.exists(backup_path):
        try:
            os.remove(backup_path)
        except Exception:
            pass
            
    logger.info("Adaptive Personalization Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_personalization_subsystems()
    sys.exit(0 if success else 1)
