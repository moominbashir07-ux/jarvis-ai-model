import time
from typing import Optional, Generator
from .base_provider import AIProvider

class OllamaProvider(AIProvider):
    """Local, offline Ollama provider running on local machine."""
    
    def __init__(self):
        super().__init__("ollama")

    def generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        start_time = time.time()
        # Simulation reasoning logic
        prompt_lower = prompt.lower()
        if "hello" in prompt_lower or "hi" in prompt_lower:
            response = "Hello, sir. Systems are online. How can I assist you today?"
        elif "status" in prompt_lower:
            response = "All modules reporting healthy. Local models running at optimal temperature."
        elif "time" in prompt_lower:
            import datetime
            now_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {now_time}."
        else:
            response = f"Local Reasoning: Analyzed prompt offline. Actions queued. (Query: {prompt})"

        self.last_latency = time.time() - start_time
        self.success_count += 1
        
        # Track simulated tokens
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        self.total_tokens_sent += input_tokens
        self.total_tokens_received += output_tokens
        self.estimate_cost(prompt, response)
        
        return f"[LOCAL] {response}"

    def stream_generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        response = self.generate(prompt, context, system_prompt)
        words = response.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            time.sleep(0.02)

    def health_check(self) -> str:
        self.health_status = "ONLINE"
        return self.health_status

    def estimate_cost(self, prompt: str, response: str) -> float:
        # Local models are completely free ($0.0)
        return 0.0
