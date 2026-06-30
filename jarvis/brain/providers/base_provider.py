import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional
from enum import Enum

class TaskType(Enum):
    CHAT = "chat"
    CODING = "coding"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    VISION = "vision"
    GENERAL = "general"

class AIProvider(ABC):
    """Abstract Base Class defining the standard contract for JARVIS AI models."""

    def __init__(self, name: str):
        self.name = name
        self.total_cost = 0.0
        self.total_tokens_sent = 0
        self.total_tokens_received = 0
        self.last_latency = 0.0
        self.success_count = 0
        self.failure_count = 0
        self.health_status = "ONLINE"  # "ONLINE", "STARTING", "DEGRADED", "OFFLINE"

    @abstractmethod
    def generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Generates a synchronous text response."""
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Streams response tokens sequentially."""
        pass

    @abstractmethod
    def health_check(self) -> str:
        """Performs diagnostic checks and returns health status: ONLINE, DEGRADED, OFFLINE."""
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str, response: str) -> float:
        """Estimates cost based on token calculations."""
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """Returns diagnostic and cost metrics for this provider."""
        return {
            "name": self.name,
            "total_cost": self.total_cost,
            "total_tokens_sent": self.total_tokens_sent,
            "total_tokens_received": self.total_tokens_received,
            "last_latency": self.last_latency,
            "success_rate": self.success_count / max(1, self.success_count + self.failure_count),
            "failure_count": self.failure_count,
            "status": self.health_status
        }
