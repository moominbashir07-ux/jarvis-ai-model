import os
import sys
import time
import logging
from jarvis.core.logger import setup_logger
from jarvis.brain.context_manager import ConversationContextManager
from jarvis.automation.sys_control import SystemController

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestContextIntelligence")

def test_context_intelligence():
    logger.info("==========================================")
    logger.info("  Context Intelligence (Phase A) Test     ")
    logger.info("==========================================")

    ctx = ConversationContextManager()

    # 1. Active App Window Context
    logger.info("Testing active application window context pings...")
    app_info = ctx.get_active_app_context()
    logger.info(f"Foreground App Info: {app_info}")
    for key in ("active", "app_name", "title", "pid", "hwnd"):
        if key not in app_info:
            logger.error(f"Missing key in active app context: {key}")
            return False

    # 2. Clipboard Sniffing Context
    logger.info("Testing clipboard content snippet retrieval...")
    ctrl = SystemController()
    ctrl.allow_unsafe = True
    token = f"Context-Token-{int(time.time())}"
    ctrl.write_clipboard(token)
    
    clip_info = ctx.get_clipboard_context()
    logger.info(f"Clipboard Context: {clip_info}")
    if not clip_info["has_text"] or clip_info["text"] != token:
        logger.error("Clipboard context text mismatch!")
        return False

    # 3. File History Logger
    logger.info("Testing rotating file interaction logs...")
    ctx.log_file_interaction("create", "src/core.py")
    ctx.log_file_interaction("write", "src/core.py")
    ctx.log_file_interaction("read", "tests/main.py")
    
    history = ctx.get_file_history()
    logger.info(f"Logged File History Size: {len(history)}")
    if len(history) != 2: # "src/core.py" (uniqued/deduplicated) and "tests/main.py"
        logger.error(f"Unexpected file history size: {len(history)}")
        return False
    logger.info(f"Latest File History Item: {history[0]}")
    if history[0]["filepath"] != "tests/main.py" or history[0]["action"] != "READ":
        logger.error("File interaction history sequence order is incorrect!")
        return False

    # 4. Synthesized Unified Context Map
    logger.info("Testing unified context synthesis payload...")
    unified = ctx.get_unified_context()
    logger.info(f"Unified Context Map Keys: {list(unified.keys())}")
    for key in ("active_application", "clipboard_snippet", "recent_file_history", "volatile_session_variables", "timestamp"):
        if key not in unified:
            logger.error(f"Missing unified context key: {key}")
            return False
            
    logger.info("Context Intelligence (Phase A) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_context_intelligence()
    sys.exit(0 if success else 1)
