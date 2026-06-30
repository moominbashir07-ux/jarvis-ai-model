import logging
import time
import re
from typing import Dict, Any, Tuple, Optional
from jarvis.config import settings
from jarvis.brain.providers.base_provider import TaskType, AIProvider

logger = logging.getLogger("JARVIS.Brain.Router")

class CircuitBreaker:
    """Implements the Circuit Breaker pattern to protect system endpoints from cascading failures."""

    def __init__(self, name: str, failure_threshold: int = 2, recovery_timeout: float = 20.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        # State machine: 'CLOSED' (working), 'OPEN' (broken, bypass), 'HALF_OPEN' (testing recovery)
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        """Determines if calls can pass through this circuit breaker."""
        if self.state == "CLOSED":
            return True
            
        current_time = time.time()
        if self.state == "OPEN":
            # Check if cooldown has expired to test recovery
            if current_time - self.last_failure_time > self.recovery_timeout:
                logger.warning(f"Circuit Breaker [{self.name}] entering HALF-OPEN state (cooldown expired). Testing recovery.")
                self.state = "HALF_OPEN"
                return True
            return False
            
        # HALF_OPEN state allows testing
        return True

    def record_success(self):
        """Resets the circuit back to CLOSED state on successful completion."""
        self.failure_count = 0
        if self.state != "CLOSED":
            logger.info(f"Circuit Breaker [{self.name}] recovered successfully! Closing circuit.")
            self.state = "CLOSED"

    def record_failure(self):
        """Logs a failure, tripping the circuit if it hits the threshold limit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(f"Circuit Breaker [{self.name}] logged failure #{self.failure_count}.")
        
        if self.failure_count >= self.failure_threshold:
            logger.critical(
                f"Circuit Breaker [{self.name}] tripped to OPEN state! "
                f"Bypassing provider calls for next {self.recovery_timeout} seconds."
            )
            self.state = "OPEN"


class TaskClassifier:
    """Classifies user queries into specific TaskTypes using structural heuristics and syntax patterns."""

    def classify(self, query: str) -> TaskType:
        query_lower = query.lower()
        
        # 1. Structural Checks for coding formatting or code symbols
        coding_signals = [
            "def ", "class ", "import ", "python", "javascript", "const ", "let ",
            "regex", "compile", "syntax", "git", "bash", "shell", "curl"
        ]
        if any(sig in query_lower for sig in coding_signals) or ("{" in query and "}" in query and ("=" in query or ";" in query)):
            return TaskType.CODING

        # 2. Automation OS Controls
        automation_signals = [
            "open", "launch", "close", "kill", "process", "volume", "folder",
            "directory", "move file", "delete", "create folder"
        ]
        if any(sig in query_lower for sig in automation_signals):
            return TaskType.AUTOMATION

        # 3. Screen or Camera Analysis (Vision)
        vision_signals = ["look at", "see", "webcam", "screenshot", "camera", "picture", "image"]
        if any(sig in query_lower for sig in vision_signals):
            return TaskType.VISION

        # 4. Web facts searches
        research_signals = ["search", "google", "find online", "weather", "news", "latest", "stock", "price"]
        if any(sig in query_lower for sig in research_signals):
            return TaskType.RESEARCH

        # 5. Data Analysis
        analysis_signals = ["analyze", "calculate", "stat", "graph", "sum", "average", "median", "plot", "trend"]
        if any(sig in query_lower for sig in analysis_signals):
            return TaskType.ANALYSIS

        # 6. Check length for General intent
        if len(query.split()) > 25:
            return TaskType.GENERAL
            
        return TaskType.CHAT


class ProviderRouter:
    """Dynamically routes task payloads to optimal AIProviders based on TaskType classification and metrics health."""

    def __init__(self, event_bus=None, health_manager=None):
        self.event_bus = event_bus
        self.health_manager = health_manager
        self.classifier = TaskClassifier()
        
        # Load providers dynamically
        from jarvis.brain.providers.ollama_provider import OllamaProvider
        from jarvis.brain.providers.openai_provider import OpenAIProvider
        from jarvis.brain.providers.gemini_provider import GeminiProvider
        
        self.providers: Dict[str, AIProvider] = {
            "ollama": OllamaProvider(),
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider()
        }
        # Legacy mappings
        self.providers["local"] = self.providers["ollama"]
        self.providers["chatgpt"] = self.providers["openai"]
        
        self.circuits = {
            "openai": CircuitBreaker(name="OpenAI-API", failure_threshold=2, recovery_timeout=20.0),
            "gemini": CircuitBreaker(name="Gemini-API", failure_threshold=2, recovery_timeout=20.0)
        }
        # Legacy mappings
        self.circuits["chatgpt"] = self.circuits["openai"]
        
        logger.debug("ProviderRouter fully initialized with provider mappings.")

    def route(self, query: str) -> AIProvider:
        """Classifies intent and routes query to the optimal healthy provider, applying circuit breakers."""
        task_type = self.classifier.classify(query)
        
        # Determine routing sequence mapping
        if task_type == TaskType.CODING:
            primary = "openai"
            fallback = "gemini"
        elif task_type in (TaskType.RESEARCH, TaskType.VISION, TaskType.ANALYSIS):
            primary = "gemini"
            fallback = "openai"
        elif task_type == TaskType.CHAT or task_type == TaskType.GENERAL:
            primary = "ollama"
            fallback = "openai"
        else:
            primary = "ollama"
            fallback = "gemini"

        # Check circuit health on primary provider
        if primary in self.circuits and not self.circuits[primary].can_execute():
            logger.warning(f"Primary provider [{primary.upper()}] circuit is OPEN. Failing over to fallback [{fallback.upper()}].")
            if self.event_bus:
                self.event_bus.publish("ProviderDegraded", {"provider": primary, "reason": "Circuit breaker open"})
            primary = fallback
            fallback = "ollama"

        # Double check fallback circuit health
        if primary in self.circuits and not self.circuits[primary].can_execute():
            primary = "ollama"

        provider = self.providers[primary]
        logger.info(f"Selected AI Provider [{provider.name.upper()}] for Task [{task_type.name}].")

        # Expose routing trace to EventBus
        if self.event_bus:
            self.event_bus.publish("AIRouteSelected", {
                "query": query,
                "task_type": task_type.value,
                "selected_provider": provider.name
            })
            
        return provider

    def classify_intent(self, query: str) -> str:
        """Legacy intent classification method for backwards compatibility."""
        task_type = self.classifier.classify(query)
        mapping = {
            TaskType.CHAT: "simple",
            TaskType.CODING: "coding",
            TaskType.RESEARCH: "web_research",
            TaskType.VISION: "vision",
            TaskType.AUTOMATION: "automation",
            TaskType.ANALYSIS: "analysis",
            TaskType.GENERAL: "simple"
        }
        return mapping.get(task_type, "simple")

    def select_model(self, query: str) -> Tuple[str, str]:
        """Legacy model selection method for backwards compatibility."""
        task_type = self.classifier.classify(query)
        if task_type == TaskType.CODING:
            primary = "chatgpt"
            fallback = "gemini"
        elif task_type in (TaskType.RESEARCH, TaskType.VISION, TaskType.ANALYSIS):
            primary = "gemini"
            fallback = "chatgpt"
        elif task_type in (TaskType.CHAT, TaskType.GENERAL):
            primary = "local"
            fallback = "chatgpt"
        else:
            primary = "local"
            fallback = "gemini"

        if primary in self.circuits and not self.circuits[primary].can_execute():
            primary = fallback
            fallback = "local"

        if primary in self.circuits and not self.circuits[primary].can_execute():
            primary = "local"

        return primary, fallback

    def record_transaction(self, provider_name: str, success: bool, latency: float = 0.0, cost: float = 0.0, tokens: int = 0, error_msg: Optional[str] = None):
        """Records metric logs to the active circuit breakers and health managers."""
        # Normalize name for health manager metrics and events
        norm_name = provider_name
        if provider_name == "chatgpt":
            norm_name = "openai"
        elif provider_name == "local":
            norm_name = "ollama"

        # 1. Update circuit status
        if provider_name in self.circuits:
            cb = self.circuits[provider_name]
            if success:
                cb.record_success()
            else:
                cb.record_failure()
                
        # 2. Update health manager stats
        if self.health_manager:
            self.health_manager.record_metrics(
                provider_name=norm_name,
                success=success,
                latency=latency,
                cost=cost,
                tokens=tokens,
                error_msg=error_msg
            )
            
            # Synchronize health manager statuses
            if provider_name in self.circuits:
                cb_state = self.circuits[provider_name].state
                if cb_state == "OPEN":
                    self.health_manager.update_provider_health(norm_name, "OFFLINE", "Circuit breaker tripped")
                elif cb_state == "HALF_OPEN":
                    self.health_manager.update_provider_health(norm_name, "DEGRADED", "Testing recovery loop")
                else:
                    self.health_manager.update_provider_health(norm_name, "ONLINE")
            else:
                self.health_manager.update_provider_health(norm_name, "ONLINE")
                
        # Set instance status directly for introspection
        if provider_name in self.providers:
            p = self.providers[provider_name]
            p.last_latency = latency
            p.total_cost += cost
            p.total_tokens_sent += tokens // 2
            p.total_tokens_received += tokens // 2
            if not success:
                p.health_status = "OFFLINE"
            else:
                p.health_status = "ONLINE"


# Alias for legacy compatibility
AIRouter = ProviderRouter

