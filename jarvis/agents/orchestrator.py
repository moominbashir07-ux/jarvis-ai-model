import logging
import time
from typing import Dict, Any, List
from jarvis.agents.base_agent import BaseAgent
from jarvis.agents.registry import agent_registry

logger = logging.getLogger("JARVIS.Orchestrator")

class CoreOrchestrator(BaseAgent):
    """Central engine coordinating planning, subtask execution context routing, and supervisor recovery checks."""

    def __init__(self):
        super().__init__(
            name="CoreOrchestrator",
            description="Coordinates cooperation between planner, memory, automation, vision, research, and conversation agents."
        )
        self.session_context: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Orchestrator received high-level goal: '{task_description}'")
        self.session_context.clear()
        self.execution_history.clear()

        planner = agent_registry.get_agent("planneragent")
        supervisor = agent_registry.get_agent("supervisoragent")
        memory_agent = agent_registry.get_agent("memoryagent")
        conv_agent = agent_registry.get_agent("conversationagent")
        
        if not planner or not supervisor:
            return {"success": False, "error": "PlannerAgent or SupervisorAgent missing from registry."}

        plan_res = planner.run(task_description)
        if not plan_res.get("success"):
            return {"success": False, "error": "Goal planning failed."}
            
        plan = plan_res["plan"]
        subtasks: List[Dict[str, Any]] = plan["subtasks"]
        logger.info(f"Formulated structured execution graph containing {len(subtasks)} subtasks.")

        completed_task_ids = set()
        
        while len(completed_task_ids) < len(subtasks):
            progress_made = False
            for task in subtasks:
                task_id = task["task_id"]
                if task["status"] == "COMPLETED" or task_id in completed_task_ids:
                    continue

                deps_resolved = all(dep in completed_task_ids for dep in task["dependencies"])
                if not deps_resolved:
                    continue

                sup_check = supervisor.run(task["description"], {"task_id": task_id, "status": "START"})
                if sup_check.get("action") == "ABORT":
                    return {"success": False, "error": "Supervisor aborted execution.", "reason": sup_check.get("reason")}

                task["status"] = "RUNNING"
                target_name = task["target_agent"]
                agent = agent_registry.get_agent(target_name)
                
                if not agent:
                    logger.error(f"Agent [{target_name}] not found in registry. Escalating fail.")
                    task["status"] = "FAILED"
                else:
                    exec_context = self._build_execution_context(task_id, task["target_agent"])
                    
                    try:
                        logger.info(f"Dispatching subtask '{task_id}' to [{agent.name}]...")
                        result = agent.run(task["description"], exec_context)
                        
                        if result.get("success"):
                            task["status"] = "COMPLETED"
                            completed_task_ids.add(task_id)
                            progress_made = True
                            
                            self.session_context[task_id] = result
                            logger.info(f"Subtask '{task_id}' completed successfully.")
                            
                            if memory_agent:
                                memory_agent.run(
                                    f"Log completed subtask {task_id}",
                                    {"action": "write", "key": f"plan_task_{task_id}", "value": "COMPLETED", "category": "general"}
                                )
                        else:
                            raise RuntimeError(result.get("error", "Unknown agent failure"))
                    except Exception as e:
                        logger.warning(f"Execution error on subtask '{task_id}': {e}")
                        task["status"] = "FAILED"

                if task["status"] == "FAILED":
                    sup_fail = supervisor.run(task["description"], {"task_id": task_id, "status": "FAILED"})
                    action = sup_fail.get("action", "ABORT")
                    
                    if action == "RETRY":
                        logger.info(f"Supervisor requested RETRY for task '{task_id}'. Resetting status to PENDING.")
                        task["status"] = "PENDING"
                        progress_made = True
                    elif action == "REPLAN":
                        logger.warning(f"Supervisor requested REPLAN due to retry exhaustion. Replanning...")
                        task["status"] = "PENDING"
                        task["description"] = f"Fallback search and research: {task['description']}"
                        progress_made = True
                    else:
                        logger.critical(f"Supervisor requested ABORT for task '{task_id}'. Aborting goal execution.")
                        return {"success": False, "error": f"Orchestrator aborted on task {task_id}.", "history": self.execution_history}

            if not progress_made:
                logger.error("Deadlock alert: Main orchestrator queue loop stalled with unresolved dependencies.")
                return {"success": False, "error": "Execution graph deadlock occurred."}

        summary_msg = f"Successfully completed goal: {task_description}."
        if conv_agent:
            conv_agent.run(summary_msg)

        return {
            "success": True,
            "goal": task_description,
            "results": self.session_context,
            "completed_tasks": list(completed_task_ids)
        }

    def _build_execution_context(self, task_id: str, target_agent: str) -> Dict[str, Any]:
        """Injects relevant session context values depending on target agent characteristics."""
        ctx = {}
        
        if task_id == "write_summary":
            research_data = self.session_context.get("research_chips", {})
            report = research_data.get("report", {})
            summary_text = report.get("executive_summary", "Factual research brief on AI Chips.")
            
            ctx["action"] = "create_file"
            ctx["filepath"] = "logs/ai_chips_brief.txt"
            ctx["content"] = f"--- JARVIS AUTOMATED BRIEF ---\nTitle: {report.get('title')}\nSummary: {summary_text}\n"
            
        elif task_id == "locate_save":
            ctx["action"] = "locate_text"
            ctx["target_text"] = "Save"
            
        elif target_agent == "researchagent":
            ctx["action"] = "research"
            
        return ctx
