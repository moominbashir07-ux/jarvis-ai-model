import unittest
import time
from jarvis.brain.providers.base_provider import TaskType
from jarvis.brain.providers.ollama_provider import OllamaProvider
from jarvis.brain.providers.openai_provider import OpenAIProvider
from jarvis.brain.providers.gemini_provider import GeminiProvider
from jarvis.brain.router import ProviderRouter, TaskClassifier, CircuitBreaker
from jarvis.core.health_manager import HealthManager
from jarvis.core.event_bus import EventBus
from jarvis.brain.brain_manager import BrainManager
from jarvis.brain.context_manager import ConversationContextManager

class TestAIProvidersAndRouting(unittest.TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.health_manager = HealthManager(event_bus=self.event_bus)
        self.router = ProviderRouter(event_bus=self.event_bus, health_manager=self.health_manager)
        self.brain = BrainManager(
            event_bus=self.event_bus,
            health_manager=self.health_manager
        )

    def test_provider_initialization_and_metrics(self):
        """Test that base provider properties and metrics estimation works correctly."""
        openai = OpenAIProvider()
        self.assertEqual(openai.name, "openai")
        self.assertEqual(openai.health_status, "ONLINE")
        
        # Test mock cost calculation
        cost = openai.estimate_cost("Write code", "Here is some code")
        # len("Write code") // 4 = 10 // 4 = 2 tokens (input)
        # len("Here is some code") // 4 = 17 // 4 = 4 tokens (output)
        # Cost = (2 * 0.005 / 1000) + (4 * 0.015 / 1000) = 0.00001 + 0.00006 = 0.00007
        self.assertAlmostEqual(cost, 0.00007, places=6)
        
        # Test metrics report structure
        metrics = openai.get_metrics()
        self.assertEqual(metrics["name"], "openai")
        self.assertIn("success_rate", metrics)
        self.assertIn("status", metrics)

    def test_task_classification(self):
        """Verify TaskClassifier accurately routes intents based on query heuristics."""
        classifier = TaskClassifier()
        
        # Coding intents
        self.assertEqual(classifier.classify("Write a python script to parse logs"), TaskType.CODING)
        self.assertEqual(classifier.classify("let x = 123;"), TaskType.CODING)
        
        # Vision intents
        self.assertEqual(classifier.classify("Look at the camera screenshot"), TaskType.VISION)
        self.assertEqual(classifier.classify("screenshot of desktop"), TaskType.VISION)
        
        # Research intents
        self.assertEqual(classifier.classify("Google the weather report online"), TaskType.RESEARCH)
        self.assertEqual(classifier.classify("find latest news online"), TaskType.RESEARCH)

        # Chat / General intents
        self.assertEqual(classifier.classify("Hello there, Jarvis!"), TaskType.CHAT)
        self.assertEqual(classifier.classify("This is a very long question that spans across multiple sentences and has a lot of words to test the classification rule for general length criteria."), TaskType.GENERAL)

    def test_circuit_breaker_failover(self):
        """Assert circuit breaker trips correctly on consecutive errors and triggers failover."""
        # 1. Normal state should be CLOSED
        cb = CircuitBreaker(name="TestBreaker", failure_threshold=2, recovery_timeout=1.0)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "CLOSED")
        
        # 2. Record failure 1
        cb.record_failure()
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "CLOSED")
        
        # 3. Record failure 2 -> should trip to OPEN
        cb.record_failure()
        self.assertFalse(cb.can_execute())
        self.assertEqual(cb.state, "OPEN")
        
        # 4. Wait for recovery timeout cooldown
        time.sleep(1.1)
        # Should enter HALF_OPEN and allow execution test
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "HALF_OPEN")
        
        # 5. Record success -> should close again
        cb.record_success()
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "CLOSED")

    def test_router_integration_failover_to_local(self):
        """Verify ProviderRouter performs fallback routing when primary circuit trips."""
        # Force failures on OpenAI
        self.router.record_transaction("openai", success=False)
        self.router.record_transaction("openai", success=False)
        
        # OpenAI circuit breaker should now be OPEN
        self.assertEqual(self.router.circuits["openai"].state, "OPEN")
        
        # Route a coding query (primary should be openai, but since it is tripped, it falls back to gemini)
        provider = self.router.route("Write some python code")
        self.assertEqual(provider.name, "gemini")

    def test_health_manager_and_event_bus(self):
        """Test health manager publishes transition events to EventBus."""
        published_events = []
        
        def on_event(event_type, payload):
            published_events.append((event_type, payload))
            
        self.event_bus.subscribe("ProviderOffline", on_event)
        self.event_bus.subscribe("ProviderOnline", on_event)
        
        # Transition from ONLINE to OFFLINE
        self.health_manager.update_provider_health("openai", "OFFLINE", "Connection timeout test")
        self.assertEqual(self.health_manager.statuses["providers"]["openai"], "OFFLINE")
        
        self.assertTrue(any(e[0] == "ProviderOffline" and e[1]["provider"] == "openai" for e in published_events))

    def test_context_manager_volatile_storage(self):
        """Assert context manager stores and clears transient session variables."""
        ctx = ConversationContextManager()
        ctx.set_variable("active_agent", "researcher")
        self.assertEqual(ctx.get_variable("active_agent"), "researcher")
        
        ctx.add_volatile_memory({"role": "system", "content": "temporary memory"})
        self.assertEqual(len(ctx.get_volatile_memories()), 1)
        
        ctx.clear_all()
        self.assertIsNone(ctx.get_variable("active_agent"))
        self.assertEqual(len(ctx.get_volatile_memories()), 0)

    def test_streaming_generation(self):
        """Assert stream_generate works and outputs chunked words."""
        ollama = OllamaProvider()
        chunks = list(ollama.stream_generate("Hello"))
        self.assertGreater(len(chunks), 0)
        self.assertTrue(any("Hello" in c or "assist" in c or "sir" in c or "Reasoning" in c for c in chunks))

    def test_streaming_generation_failure_trips_circuit(self):
        """Assert that stream generation failures are recorded and trip the circuit breaker."""
        # 1. Reset circuits
        self.brain.router.circuits["openai"].state = "CLOSED"
        self.brain.router.circuits["openai"].failure_count = 0
        
        # 2. Consume a stream designed to fail
        chunks = list(self.brain.generate_response_stream("python script trigger_openai_fail"))
        
        # Verify the circuit breaker logged failure and tripped to OPEN
        self.assertEqual(self.brain.router.circuits["openai"].state, "OPEN")

if __name__ == "__main__":
    unittest.main()
