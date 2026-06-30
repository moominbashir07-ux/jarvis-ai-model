import logging
import time
from typing import List, Dict, Any, Optional
from jarvis.config import settings
from jarvis.brain.router import ProviderRouter, TaskType
from jarvis.brain.context_manager import ConversationContextManager

logger = logging.getLogger("JARVIS.Brain")

class BrainManager:
    """Manages system prompts, context aggregation, LLM completions, and query routing."""

    def __init__(self, event_bus=None, memory_manager=None, context_manager=None, health_manager=None):
        self.event_bus = event_bus
        self.memory = memory_manager
        self.health_manager = health_manager
        self.context_manager = context_manager or ConversationContextManager()
        self.router = ProviderRouter(event_bus=self.event_bus, health_manager=self.health_manager)
        
        self.system_prompt = (
            "You are JARVIS, a highly advanced personal AI OS operating system. "
            "Help the user automate Windows operations, answer queries, and coordinate agents. "
            "Keep responses concise, helpful, and sophisticated."
        )
        logger.debug("BrainManager instance initialized with routing and context layers.")

    def initialize(self):
        """Initializes API client connections (e.g. OpenAI, Anthropic, Gemini)."""
        logger.info("Initializing Brain Reasoning Engine...")
        
        # Verify API setups
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            logger.warning("OpenAI API key not configured. Cloud GPT models will default to fallback.")
        else:
            logger.info("OpenAI API configurations loaded.")
            
        if not settings.anthropic_api_key or settings.anthropic_api_key == "your_anthropic_api_key_here":
            logger.debug("Anthropic API key not configured.")
        else:
            logger.info("Anthropic API configurations loaded.")

    def generate_response(self, user_query: str, context: List[Dict[str, Any]] = None) -> str:
        """Determines best model using routing, executes model call, handles API failures and fallbacks."""
        logger.debug(f"Generating completion for query: '{user_query}'")
        
        # 1. Select optimal provider
        provider = self.router.route(user_query)
        
        # Determine fallback chain (openai -> gemini -> ollama)
        chain = ["openai", "gemini", "ollama"]
        # Start chain at the selected provider name
        selected_name = "openai" if provider.name == "chatgpt" else ("ollama" if provider.name == "local" else provider.name)
        if selected_name in chain:
            start_idx = chain.index(selected_name)
            fallback_chain = chain[start_idx:]
        else:
            fallback_chain = [selected_name] + chain
            
        response = None
        
        # Try each provider in the fallback chain
        for provider_name in fallback_chain:
            # Skip if circuit is OPEN (unless it's ollama, which is offline/local and has no breaker)
            if provider_name in self.router.circuits and not self.router.circuits[provider_name].can_execute():
                logger.warning(f"Circuit is OPEN for provider [{provider_name.upper()}]. Skipping.")
                continue
                
            active_provider = self.router.providers.get(provider_name)
            if not active_provider:
                continue
                
            start_time = time.time()
            try:
                # Compile context if needed
                context_str = str(context) if context else None
                # Generate response
                response = active_provider.generate(
                    prompt=user_query,
                    context=context_str,
                    system_prompt=self.system_prompt
                )
                latency = time.time() - start_time
                cost = active_provider.estimate_cost(user_query, response)
                tokens = (len(user_query) + len(response)) // 4
                
                # Record successful transaction
                self.router.record_transaction(
                    provider_name=provider_name,
                    success=True,
                    latency=latency,
                    cost=cost,
                    tokens=tokens
                )
                break
            except Exception as e:
                latency = time.time() - start_time
                logger.error(
                    f"Model provider [{provider_name.upper()}] API failed: {e}. "
                    "Initiating fallback sequence..."
                )
                # Record failed transaction
                self.router.record_transaction(
                    provider_name=provider_name,
                    success=False,
                    latency=latency,
                    error_msg=str(e)
                )
                
        if response is None:
            logger.critical("All provider fallbacks failed!")
            response = "I apologize, sir. All cloud and local cognitive model networks are currently unreachable."
            
        return response

    def generate_response_stream(self, user_query: str, context: List[Dict[str, Any]] = None):
        """Streams response tokens sequentially for low-latency visual HUD rendering."""
        logger.debug(f"Streaming completion for query: '{user_query}'")
        provider = self.router.route(user_query)
        provider_name = provider.name
        
        # Try to stream from selected provider
        success = False
        start_time = time.time()
        full_reply = []
        try:
            # Let's verify if the provider's circuit is open before calling stream
            if provider_name in self.router.circuits and not self.router.circuits[provider_name].can_execute():
                raise RuntimeError(f"Circuit for {provider_name} is OPEN.")
                
            context_str = str(context) if context else None
            generator = provider.stream_generate(
                prompt=user_query,
                context=context_str,
                system_prompt=self.system_prompt
            )
            for chunk in generator:
                full_reply.append(chunk)
                yield chunk
            success = True
            
            # Record successful streaming transaction
            latency = time.time() - start_time
            cost = provider.estimate_cost(user_query, "".join(full_reply))
            tokens = (len(user_query) + len("".join(full_reply))) // 4
            self.router.record_transaction(
                provider_name=provider_name,
                success=True,
                latency=latency,
                cost=cost,
                tokens=tokens
            )
        except Exception as e:
            logger.warning(f"Streaming failed for provider {provider.name}: {e}. Falling back to sync generate response.")
            # Record failed transaction
            latency = time.time() - start_time
            self.router.record_transaction(
                provider_name=provider_name,
                success=False,
                latency=latency,
                error_msg=str(e)
            )
            
            # If we already yielded some chunks, do not fall back to avoid scrambled output.
            # Only do fallback if we failed before yielding anything.
            if not full_reply:
                full_response = self.generate_response(user_query, context)
                words = full_response.split(" ")
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    yield chunk
                    time.sleep(0.02)

    def cleanup(self):
        """Clean up brain manager state."""
        logger.debug("BrainManager cleanup completed.")

