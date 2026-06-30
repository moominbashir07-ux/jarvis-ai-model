import sys
import logging
from jarvis.config import settings
from jarvis.core.logger import setup_logger
from jarvis.core.orchestrator import Orchestrator

def main():
    """Main startup bootloader sequence for JARVIS AI OS."""
    
    # 1. Initialize logging
    logger = setup_logger(
        log_level_str=settings.log_level,
        logs_dir=settings.logs_dir
    )
    
    logger.info("========================================")
    logger.info("   Starting JARVIS AI OS Boot Sequence   ")
    logger.info("========================================")
    logger.info(f"Loaded Profile: {settings.env.upper()}")
    
    orchestrator = None
    try:
        # 2. Instantiate core mediator
        orchestrator = Orchestrator()
        
        # 3. Initialize all modules
        orchestrator.initialize()
        
        # 4. Start the interactive UI loop
        orchestrator.ui.start_loop()
        
    except Exception as e:
        logger.critical(f"Unhandled exception during boot sequence: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        if orchestrator:
            orchestrator.shutdown()
        logger.info("JARVIS AI OS session terminated.")

if __name__ == "__main__":
    main()
