import logging
from jarvis.config import settings
from jarvis.core.event_bus import EventBus

# Setup logger for the module
logger = logging.getLogger("JARVIS.Orchestrator")

class Orchestrator:
    """Central Mediator/Orchestrator pattern for coordinating modular JARVIS services."""

    def __init__(self):
        self.is_running = False
        self.event_bus = EventBus()
        
        # Declarative components (instantiated in initialize)
        self.brain = None
        self.memory = None
        self.stt = None
        self.tts = None
        self.listener = None
        self.vision = None
        self.automation = None
        self.ui = None
        self.ipc = None
        self.health_manager = None
        self.context_manager = None
        self.command_registry = None
        self.self_test = None
        
        logger.debug("Orchestrator initialized. Components are registered.")

    def initialize(self):
        """Instantiates and wires together all core system modules."""
        logger.info("Initializing JARVIS components...")

        # Import modules locally to avoid circular dependencies
        from jarvis.brain.brain_manager import BrainManager
        from jarvis.memory.memory_manager import MemoryManager
        from jarvis.voice.stt import SpeechToText
        from jarvis.voice.tts import TextToSpeech
        from jarvis.voice.wake_word import WakeWordEngine
        from jarvis.vision.vision_manager import VisionManager
        from jarvis.automation.sys_control import SystemController
        from jarvis.ui.gui_manager import GuiManager
        from jarvis.core.ipc_server import IPCServer
        from jarvis.core.health_manager import HealthManager
        from jarvis.brain.context_manager import ConversationContextManager

        try:
            # Setup health manager and context manager
            self.health_manager = HealthManager(event_bus=self.event_bus)
            self.context_manager = ConversationContextManager()

            # Setup Memory layer first since other components depend on history/context
            self.memory = MemoryManager(event_bus=self.event_bus)
            self.memory.initialize()

            # Setup local WebSocket IPC Server
            self.ipc = IPCServer(port=8765, event_bus=self.event_bus, orchestrator=self)
            self.ipc.start()

            # Setup AI Brain reasoning
            self.brain = BrainManager(
                event_bus=self.event_bus,
                memory_manager=self.memory,
                context_manager=self.context_manager,
                health_manager=self.health_manager
            )
            self.brain.initialize()

            # Setup Voice (STT & TTS)
            self.stt = SpeechToText()
            self.tts = TextToSpeech(event_bus=self.event_bus)
            self.stt.initialize()
            self.tts.initialize()

            # Setup Windows Automation controls
            self.automation = SystemController(event_bus=self.event_bus)
            self.automation.initialize()

            # Setup Command Registry and Self-Test Manager
            from jarvis.automation.command_registry import CommandRegistry
            from jarvis.core.self_test import SystemSelfTestManager
            
            self.command_registry = CommandRegistry(self.automation)
            self.self_test = SystemSelfTestManager(self)

            # Setup Voice Continuous Listener
            self.listener = WakeWordEngine(stt=self.stt, tts=self.tts, on_wake_callback=self._handle_wake_word_trigger)
            self.listener.initialize()
            self.listener.start()

            # Setup Vision analysis
            self.vision = VisionManager()
            self.vision.initialize()

            # Setup the UI wrapper
            self.ui = GuiManager(orchestrator=self)
            self.ui.initialize()

            # Run startup diagnostic self-tests
            self.self_test.run_all_tests()

            # Register dynamic memory handlers on the event bus
            if hasattr(self.memory, "_on_automation_finished"):
                self.event_bus.subscribe("AutomationFinished", self.memory._on_automation_finished)

            self.is_running = True
            logger.info("All JARVIS components initialized successfully.")
            
        except Exception as e:
            logger.critical(f"Critical error initializing components: {e}", exc_info=True)
            self.shutdown()
            raise

    def process_input(self, user_text: str, source: str = "text") -> str:
        """Processes user input through the core AI flow.
        
        Flow: Input -> Short term memory -> Brain (LLM) -> TTS Output -> Automation (optional) -> UI display
        """
        logger.info(f"Received input from [{source}]: '{user_text}'")

        try:
            # 1. Update Short Term Memory with User Query
            self.memory.save_interaction(role="user", content=user_text)

            # 2. Get active context
            context = self.memory.get_recent_interactions(limit=5)

            # Intercept with CommandRegistry
            if self.command_registry:
                matched_command = self.command_registry.execute(user_text)
                if matched_command is not None:
                    success, response_text = matched_command
                    # Save response to memory
                    self.memory.save_interaction(role="jarvis", content=response_text)
                    self.event_bus.publish("ThinkingStarted")
                    self.event_bus.publish("ThinkingStopped")
                    self.event_bus.publish("ResponseComplete", {"response": response_text})
                    
                    if settings.voice_enabled and source != "silent":
                        self.tts.speak(response_text)
                    return response_text

            # 3. Brain processes query using memory context
            # 3. Brain processes query in streaming mode (Phase F)
            self.event_bus.publish("ThinkingStarted")
            
            full_response_list = []
            for chunk in self.brain.generate_response_stream(user_text, context=context):
                full_response_list.append(chunk)
                self.event_bus.publish("TokenChunk", {"chunk": chunk})
                
            response_text = "".join(full_response_list)
            self.event_bus.publish("ThinkingStopped")
            self.event_bus.publish("ResponseComplete", {"response": response_text})

            # 4. Save response to memory
            self.memory.save_interaction(role="jarvis", content=response_text)

            # 5. Output response via voice if enabled
            if settings.voice_enabled and source != "silent":
                self.tts.speak(response_text)

            # 6. Check if Brain triggered any OS execution patterns (mock implementation)
            if "run command" in response_text.lower() or "open application" in response_text.lower():
                logger.info("Automation trigger detected in brain response. Delegating to Automation Manager.")
                self.automation.open_app("calc.exe")

            return response_text

        except Exception as e:
            error_msg = f"Error processing user query: {e}"
            logger.error(error_msg, exc_info=True)
            return f"I apologize, but I encountered an internal error: {error_msg}"

    def _handle_wake_word_trigger(self):
        """Callback triggered when the WakeWordEngine identifies the activation keyword."""
        self.event_bus.publish("WakeDetected")
        logger.info("Wake word matched! Processing vocal stream input...")
        
        # Stop wake word stream in WakeWordEngine before listening starts to release mic lock
        if self.listener:
            self.listener.suspend_stream()

        # Stop active speaking, and confirm wake word via audio response
        self.tts.stop()
        
        import random
        greetings = ["Yes Momin, what's up?", "Yes, sir?", "How can I assist?"]
        greeting = random.choice(greetings)
        self.tts.speak(greeting)
        
        # Wait until SAPI5 finishes speaking confirmation (or max 1.5 seconds)
        import time
        start_wait = time.time()
        while self.tts.is_speaking and (time.time() - start_wait < 1.5):
            time.sleep(0.05)
            
        # Await request
        self.event_bus.publish("ListeningStarted")
        query = self.stt.listen_and_transcribe(timeout=5.0)
        self.event_bus.publish("ListeningStopped", {"query": query or ""})
            
        if query:
            # Process in thread to avoid blocking audio handlers
            threading = __import__('threading')
            threading.Thread(
                target=self.process_input,
                args=(query, "voice"),
                daemon=True
            ).start()
        else:
            logger.debug("Wake command prompt timed out without query.")
            
        # Re-enable/resume wake-word engine stream
        if self.listener and self.listener._pyaudio:
            self.listener.resume_stream(self.listener._pyaudio)

    def shutdown(self):
        """Gracefully shuts down all components."""
        logger.info("Initiating system shutdown...")
        self.is_running = False
        
        # Shutdown in reverse dependencies order
        if self.ipc:
            self.ipc.stop()
        if self.listener:
            self.listener.stop()
        if self.ui:
            self.ui.cleanup()
        if self.automation:
            self.automation.cleanup()
        if self.vision:
            self.vision.cleanup()
        if self.stt:
            self.stt.cleanup()
        if self.tts:
            self.tts.cleanup()
        if self.brain:
            self.brain.cleanup()
        if self.memory:
            self.memory.cleanup()
            
        logger.info("JARVIS AI OS shutdown complete.")
