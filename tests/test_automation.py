import os
import time
import logging
from pathlib import Path
from jarvis.core.logger import setup_logger
from jarvis.automation.sys_control import SystemController
from jarvis.memory.memory_manager import MemoryManager

# Setup basic logging to console
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestAutomation")

def test_automation_lifecycle():
    logger.info("--- Starting Windows Automation Engine Verification ---")
    
    # Initialize Memory manager to audit logs
    memory = MemoryManager()
    memory.db_path = "jarvis_test_memory.db"
    if os.path.exists("jarvis_test_memory.db"):
        try:
            os.remove("jarvis_test_memory.db")
        except Exception:
            pass
    memory.initialize()

    # Disable unsafe execution to test permission prompts
    controller = SystemController(memory_manager=memory)
    
    # 1. Verify Permission checks
    logger.info("Verifying permission level checks...")
    perm_vol = controller.check_permission("adjust_volume")
    perm_move = controller.check_permission("move_file")
    logger.info(f"Volume Permission: {perm_vol} (Expected: ALLOW)")
    logger.info(f"Move File Permission: {perm_move} (Expected: PROMPT)")
    
    if perm_vol != "ALLOW" or perm_move != "PROMPT":
        logger.error("Permission check logic failed!")
        return False

    # Temporarily force allow dangerous actions to test file operations
    controller.allow_unsafe = True

    # 2. Test folder creation
    logger.info("Testing folder creation...")
    test_dir = "tests/temp_test_dir"
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    success, msg = controller.create_folder(test_dir)
    logger.info(f"Create Folder Result: {success} ({msg})")
    
    if not success or not Path(test_dir).exists():
        logger.error("Folder creation failed!")
        return False

    # 3. Test file creation and move
    logger.info("Testing file move operations...")
    dummy_file = f"{test_dir}/dummy_file.txt"
    Path(dummy_file).write_text("Hello, JARVIS!")
    
    target_dest = f"{test_dir}/moved_dummy.txt"
    success, msg = controller.move_file(dummy_file, target_dest)
    logger.info(f"Move File Result: {success} ({msg})")
    
    if not success or not Path(target_dest).exists() or Path(dummy_file).exists():
        logger.error("File move failed!")
        return False

    # 4. Test Undo / Transaction Recovery
    logger.info("Executing recovery undo on moved file...")
    undo_success, undo_msg = controller.execute_undo()
    logger.info(f"Undo Result: {undo_success} ({undo_msg})")
    
    if not undo_success or not Path(dummy_file).exists() or Path(target_dest).exists():
        logger.error("Undo move failed!")
        return False

    # 5. Clean up folder undo
    logger.info("Executing folder creation undo...")
    undo_success2, undo_msg2 = controller.execute_undo()
    logger.info(f"Folder Undo Result: {undo_success2} ({undo_msg2})")
    
    if Path(test_dir).exists():
        logger.error("Folder cleanup undo failed!")
        return False

    # 6. Test Screen capture
    logger.info("Testing screen capture screenshot utility...")
    sc_success, sc_path = controller.capture_screenshot("tests")
    logger.info(f"Screenshot Captured: {sc_success} (Saved to: {sc_path})")
    
    if sc_success and Path(sc_path).exists():
        # Clean up test screenshot
        os.remove(sc_path)
    else:
        logger.error("Screenshot capture failed!")
        return False

    # 7. Test Clipboard operations
    logger.info("Testing Clipboard Operations...")
    clip_text = f"JARVIS CLIPBOARD TEST: {int(time.time())}"
    ok_write, msg_write = controller.write_clipboard(clip_text)
    logger.info(f"Write Clipboard: {ok_write} ({msg_write})")
    if not ok_write:
        logger.error("Failed to write to clipboard!")
        return False
        
    ok_read, data_read = controller.read_clipboard()
    logger.info(f"Read Clipboard: {ok_read} (Data: '{data_read}')")
    if not ok_read or data_read != clip_text:
        logger.error("Clipboard verification failed (mismatch or read error)!")
        return False
        
    ok_clear, msg_clear = controller.clear_clipboard()
    logger.info(f"Clear Clipboard: {ok_clear} ({msg_clear})")
    if not ok_clear:
        logger.error("Failed to clear clipboard!")
        return False
        
    ok_read2, data_read2 = controller.read_clipboard()
    if data_read2 == clip_text:
        logger.error("Failed to clear clipboard data!")
        return False

    # 8. Test Advanced File operations
    logger.info("Testing Advanced File Creation & Recycle Bin Deletion...")
    adv_file = f"{test_dir}_adv/test_file.txt"
    ok_create, msg_create = controller.create_file(adv_file, "Advanced test content")
    logger.info(f"Create File: {ok_create} ({msg_create})")
    if not ok_create or not Path(adv_file).exists():
        logger.error("Failed to create file via SystemController!")
        return False
        
    # Verify undo file creation
    logger.info("Verifying advanced file creation undo...")
    ok_undo, msg_undo = controller.execute_undo()
    logger.info(f"Undo File Creation: {ok_undo} ({msg_undo})")
    if not ok_undo or Path(adv_file).exists():
        logger.error("Failed to undo file creation!")
        return False
        
    # Re-create file for deletion test
    controller.create_file(adv_file, "Advanced test content")
    
    # Delete to Recycle Bin
    ok_del, msg_del = controller.delete_file_path(adv_file, use_recycle_bin=True)
    logger.info(f"Delete to Recycle Bin: {ok_del} ({msg_del})")
    if not ok_del or Path(adv_file).exists():
        logger.error("Failed to delete file to Recycle Bin!")
        return False
        
    # Clean up test dir permanently
    controller.delete_file_path(f"{test_dir}_adv", use_recycle_bin=False)

    # 9. Test Window Enumeration
    logger.info("Testing Window Enumeration...")
    ok_enum, app_list = controller.get_running_apps()
    logger.info(f"Enumerated visible windows: {ok_enum} (Count: {len(app_list)})")
    if not ok_enum:
        logger.error("Failed to enumerate visible windows!")
        return False
        
    # Verify we can find some window
    if len(app_list) > 0:
        target_hwnd = app_list[0]["hwnd"]
        logger.info(f"Testing window restore action on handle: {target_hwnd}")
        ok_win, msg_win = controller.control_app_window(target_hwnd, "restore")
        logger.info(f"Restore Window Control: {ok_win} ({msg_win})")
        if not ok_win:
            logger.error("Failed to execute window state control!")
            return False

    # 10. Verify memory audits
    logger.info("Verifying SQL database audit logs...")
    cursor = memory.conn.cursor()
    cursor.execute("SELECT action_name, execution_status FROM automation_logs")
    rows = cursor.fetchall()
    logger.info(f"Audit Log Entries Written: {len(rows)}")
    for row in rows:
         logger.info(f" - Logged Action: {row[0]} | Status: {row[1]}")

    memory.cleanup()
    logger.info("Automation Engine Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS Windows Control Engine Tests     ")
    logger.info("==========================================")
    
    test_automation_lifecycle()
