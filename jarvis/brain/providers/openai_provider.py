import time
from typing import Optional, Generator
from .base_provider import AIProvider
from jarvis.config import settings

class OpenAIProvider(AIProvider):
    """Cloud OpenAI provider hosting advanced GPT model endpoints."""
    
    def __init__(self):
        super().__init__("openai")

    def generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        # Simulation helper to test failovers and circuit-breaker states
        if "trigger_fail" in prompt.lower() or "trigger_openai_fail" in prompt.lower():
            self.failure_count += 1
            raise RuntimeError("API Connection Timeout: OpenAI host unreachable.")

        start_time = time.time()
        
        # Implement a retry loop (Phase 2 requirement)
        retries = 2
        for attempt in range(retries + 1):
            try:
                # Simulate call delay (API request roundtrip)
                time.sleep(0.05)
                response = f"Coding Assistant: I have formatted the script block for query: '{prompt}'."
                break
            except Exception as e:
                if attempt == retries:
                    self.failure_count += 1
                    raise e
                time.sleep(0.1)

        self.last_latency = time.time() - start_time
        self.success_count += 1
        
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        self.total_tokens_sent += input_tokens
        self.total_tokens_received += output_tokens
        cost = self.estimate_cost(prompt, response)
        self.total_cost += cost
        
        return f"[OPENAI] {response}"

    def stream_generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        # Handle failures in stream too
        if "trigger_fail" in prompt.lower() or "trigger_openai_fail" in prompt.lower():
            self.failure_count += 1
            raise RuntimeError("API Connection Timeout: OpenAI stream unreachable.")
            
        # Re-use generate response logic
        response = self.generate(prompt, context, system_prompt)
        words = response.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            time.sleep(0.02)

    def health_check(self) -> str:
        # Check settings for API keys
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            self.health_status = "DEGRADED"
        else:
            self.health_status = "ONLINE"
        return self.health_status

    def estimate_cost(self, prompt: str, response: str) -> float:
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        cost = (input_tokens * 0.005 / 1000) + (output_tokens * 0.015 / 1000)
        return cost
