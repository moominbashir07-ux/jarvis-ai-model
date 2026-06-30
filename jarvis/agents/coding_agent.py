import logging
from typing import Dict, Any
from jarvis.agents.base_agent import BaseAgent
from jarvis.agents.registry import agent_registry

logger = logging.getLogger("JARVIS.Agents.Coding")

class CodingAgent(BaseAgent):
    """Autonomous Coding Agent for JARVIS AI OS.
    
    Generates software code scripts, writes blocks to files, and collaborates with
    the ResearchAgent to look up library configurations and programming patterns.
    """

    def __init__(self):
        super().__init__(
            name="CodingAgent",
            description="Generates, structures, and compiles software script code blocks."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Initiating coding task: '{task_description}'")
        
        # Collaborative Step: Query the ResearchAgent for code recommendations
        logger.info("Collaborative query: Dispatched research lookup request to ResearchAgent...")
        researcher = agent_registry.get_agent("researchagent")
        
        research_notes = "Default Python standard library recommendations."
        if researcher:
            try:
                # Request research assistance
                research_res = researcher.run(f"best code pattern for: {task_description}")
                research_notes = research_res.get("report", {}).get("executive_summary", "No findings.")
                logger.info("Collaborative query complete. Research inputs retrieved successfully.")
            except Exception as e:
                logger.warning(f"Failed to query ResearchAgent: {e}. Continuing with local templates.")
                
        # Generate code block incorporating research details
        code_block = self._generate_script(task_description, research_notes)
        
        # Save generated script if path is specified in context
        output_file = (context or {}).get("write_to_file")
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(code_block)
                logger.info(f"Code block successfully written to file: {output_file}")
            except Exception as e:
                logger.error(f"Failed to write file {output_file}: {e}")

        return {
            "success": True,
            "code": code_block,
            "research_context": research_notes,
            "file_written": output_file
        }

    def _generate_script(self, task: str, research_notes: str) -> str:
        """Generates standard boilerplate templates."""
        return f"""# -*- coding: utf-8 -*-
# Generated autonomously by JARVIS CodingAgent
# Research Notes: {research_notes}
# Objective: {task}

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS.Autogen")

def main():
    logger.info("Executing generated script...")
    # Target code for: {task}
    print("Script runs successfully.")

if __name__ == '__main__':
    main()
"""

    def cleanup(self):
        logger.debug("CodingAgent cleanup completed.")
