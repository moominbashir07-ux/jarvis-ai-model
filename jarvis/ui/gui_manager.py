import logging
import sys
import time
from colorama import Fore, Style
from jarvis.config import settings

logger = logging.getLogger("JARVIS.UI")

class GuiManager:
    """Manages the UI presentation layer, defaulting to an interactive console dashboard."""

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        logger.debug("GuiManager initialized.")

    def initialize(self):
        """Initializes UI hooks (e.g. GUI frames or command shell lines)."""
        logger.info("Initializing Interface presentation layer...")

    def start_loop(self):
        """Runs the primary interaction loop.
        
        Reads user CLI inputs, dispatches them through the Orchestrator,
        and renders responses with clean, structured styling.
        """
        self._print_banner()
        
        is_interactive = sys.stdin.isatty()
        if not is_interactive:
            logger.info("Non-interactive terminal detected. CLI input disabled. Running in daemon mode.")
        
        try:
            while self.orchestrator.is_running:
                if not is_interactive:
                    time.sleep(1.0)
                    continue
                    
                # Custom styled prompt
                prompt = f"\n{Fore.CYAN}JARVIS {Fore.YELLOW}» {Style.RESET_ALL}"
                
                try:
                    user_input = input(prompt).strip()
                except (KeyboardInterrupt, EOFError):
                    print(f"\n{Fore.RED}[INFO] Exiting interactive shell.")
                    break
                
                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit", "shutdown", "bye"):
                    print(f"\n{Fore.GREEN}Shutting down JARVIS. Good bye, sir.{Style.RESET_ALL}")
                    break

                # Process input through the orchestrator
                response = self.orchestrator.process_input(user_input, source="cli")
                
                # Output formatted response bubble
                print(f"{Fore.GREEN}JARVIS: {Style.BRIGHT}{response}{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Error in UI event loop: {e}", exc_info=True)
        finally:
            self.orchestrator.shutdown()

    def _print_banner(self):
        """Prints a styled startup banner to wow the user."""
        banner = fr"""
{Fore.CYAN}===================================================================
      __ ___  ____ _   __ ____ _____     ___     ____  ____ 
   / / / _ \/ __ \ | / /  _ // ___/    / _ \   / __ \/ __/ 
 _/ / / __ / /_/ / |/ / _/_ // /__    / ___ \ / /_/ /\ \   
 \__/ /_/ /_/\____/\___//____/\____/   /_/   /_/\____/___/  
                                                            
==================================================================={Style.RESET_ALL}
  System Status: {Fore.GREEN}ONLINE{Style.RESET_ALL} | Environment: {Fore.YELLOW}{settings.env.upper()}{Style.RESET_ALL} | Log Level: {Fore.MAGENTA}{settings.log_level}{Style.RESET_ALL}
  Type {Fore.LIGHTBLUE_EX}'exit'{Style.RESET_ALL} to terminate the environment session.
===================================================================
"""
        print(banner)

    def cleanup(self):
        """Cleans up UI handles."""
        logger.debug("GuiManager window handles released.")
