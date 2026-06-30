import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows-compatible console colors
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom logging formatter that adds terminal coloring to log levels."""
    
    COLORS = {
        logging.DEBUG: Fore.BLUE + Style.BRIGHT,
        logging.INFO: Fore.GREEN + Style.BRIGHT,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.WHITE + Back.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        if color:
            # Colorize the [LEVEL] section or the whole log line
            levelname = record.levelname
            message = message.replace(levelname, f"{color}{levelname}{Style.RESET_ALL}")
        return message

def setup_logger(log_level_str: str = "INFO", logs_dir: Path = None) -> logging.Logger:
    """Sets up a root logger with file rotation and colored console output."""
    
    # Map string log level to logging constant
    level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Root logger configuration
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter definitions
    log_format = "[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Console Handler (Colored)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating)
    if logs_dir:
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "jarvis.log"
        
        # Keep up to 5 backups of 5MB each
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
