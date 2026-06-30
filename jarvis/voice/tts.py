import logging
import os
import queue
import threading
import time
from typing import Optional
from jarvis.config import settings

logger = logging.getLogger("JARVIS.Voice.TTS")

# Optional imports for system/cloud speech synthesis
pyttsx3_available = False
try:
    import pyttsx3
    pyttsx3_available = True
except ImportError:
    pass

class TextToSpeech:
    """Thread-safe Text-to-Speech Engine with queue processing and speech interruption support."""

    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.enabled = settings.voice_enabled
        self.provider = settings.voice_provider
        self.voice_id = settings.voice_id
        
        # Thread-safety mechanics
        self.speak_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
        self.engine_lock = threading.Lock()
        
        # Interrupt control
        self.interrupt_event = threading.Event()
        self.is_speaking = False
        
        # Native engine reference
        self.engine = None
        logger.debug(f"TTS Engine initialized with provider '{self.provider}'.")

    def initialize(self) -> bool:
        """Starts background TTS worker thread and boots selected speech engine."""
        if not self.enabled:
            logger.info("TTS is disabled in configuration settings.")
            return False

        logger.info(f"Booting Text-to-Speech worker engine using [{self.provider}]...")
        self.is_running = True
        
        # Spawns thread-safe worker queue listener
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True, name="JARVIS-TTS-Worker")
        self.worker_thread.start()
        return True

    def speak(self, text: str):
        """Pushes text into the background worker queue."""
        if not self.enabled or not text:
            return
        logger.debug(f"Queuing text for speech: '{text}'")
        self.speak_queue.put(text)

    def stop(self):
        """Interrupts active speaking session immediately and flushes the buffer queue."""
        if not self.is_speaking and self.speak_queue.empty():
            return
            
        logger.warning("Vocal output interrupt signal received! Flushing speech buffer.")
        self.interrupt_event.set()
        
        # Clear items in queue
        while not self.speak_queue.empty():
            try:
                self.speak_queue.get_nowait()
                self.speak_queue.task_done()
            except queue.Empty:
                break
                
        # Call stop on native engine
        if self.engine:
            with self.engine_lock:
                try:
                    self.engine.stop()
                except Exception as e:
                    logger.debug(f"Non-critical engine stop error: {e}")
                    
        self.is_speaking = False

    def _speech_worker(self):
        """Background worker thread loop that pulls and processes text from the queue."""
        # Initialize native Windows engine in the worker thread to prevent cross-thread COM issues
        if self.provider == "system":
            try:
                import pythoncom
                pythoncom.CoInitialize()
                logger.debug("COM Library initialized on TTS background worker thread.")
            except Exception as e:
                logger.debug(f"Non-critical COM CoInitialize failure: {e}")

            if pyttsx3_available:
                try:
                    self.engine = pyttsx3.init()
                    self.engine.setProperty("rate", 175)  # Set spoken words per minute
                    
                    # Log available voices for debugging
                    voices = self.engine.getProperty("voices")
                    if voices:
                        logger.debug(f"Windows system speech engine loaded with {len(voices)} voices.")
                except Exception as e:
                    logger.error(f"Failed to instantiate native pyttsx3 speaker: {e}. Falling back to simulation mode.")
                    self.engine = None
            else:
                logger.warning("pyttsx3 is not installed. TTS running in mock stdout mode.")

        while self.is_running:
            try:
                # Wait for text to speak (blocking for 0.5s to check shutdown state)
                text = self.speak_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            self.interrupt_event.clear()
            self.is_speaking = True
            
            # Fire SpeakingStarted event dynamically on the EventBus
            if getattr(self, "event_bus", None):
                self.event_bus.publish("SpeakingStarted", {"response": text})
            
            try:
                if self.provider == "system" and self.engine:
                    self._speak_system(text)
                elif self.provider == "elevenlabs" and settings.elevenlabs_api_key:
                    self._speak_elevenlabs(text)
                else:
                    self._speak_mock(text)
            except Exception as e:
                logger.error(f"Error occurred during speech synthesis: {e}", exc_info=True)
            finally:
                self.is_speaking = False
                
                # Fire SpeakingStopped event dynamically on the EventBus
                if getattr(self, "event_bus", None):
                    self.event_bus.publish("SpeakingStopped", {"response": text})
                
                self.speak_queue.task_done()

    def _speak_system(self, text: str):
        """Synthesizes text using native Windows SAPI5 via pyttsx3."""
        logger.debug(f"Synthesizing offline native speech: '{text}'")
        
        # Check interrupt event before initiating engine
        if self.interrupt_event.is_set():
            return

        with self.engine_lock:
            try:
                self.engine.say(text)
                # Run the speech event loop. It blocks until complete or engine.stop() is called
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Native Windows TTS run error: {e}")

    def _speak_elevenlabs(self, text: str):
        """Synthesizes high-quality speech via ElevenLabs API."""
        logger.info(f"Requesting cloud ElevenLabs audio for: '{text}'")
        
        # Check interrupt event
        if self.interrupt_event.is_set():
            return
            
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=settings.elevenlabs_api_key)
            
            # Simple API voice synthesis call
            audio_generator = client.generate(
                text=text,
                voice=self.voice_id or "Rachel",
                model="eleven_monolingual_v1"
            )
            
            # Write to temporary file and play (simulated placeholder for latency check)
            logger.info("ElevenLabs Cloud TTS buffer retrieved. Initiating speaker channels...")
            # In production: play(audio_generator)
            self._speak_mock(text)
        except Exception as e:
            logger.error(f"ElevenLabs Cloud TTS generation failed: {e}. Falling back to mock speaker.")
            self._speak_mock(text)

    def _speak_mock(self, text: str):
        """Developer mock speaker output that outputs to the console directly."""
        # Simulate spoken words speed delay (150 words per minute => ~2.5 words per second)
        word_count = len(text.split())
        sleep_duration = max(1.0, word_count / 2.5)
        
        print(f"\n📢 [JARVIS]: \"{text}\"\n")
        
        # Sleep in small slices to monitor user interrupt trigger mid-speech
        slice_count = int(sleep_duration / 0.1)
        for _ in range(slice_count):
            if self.interrupt_event.is_set():
                logger.debug("Mock speech output interrupted mid-sentence.")
                break
            time.sleep(0.1)

    def cleanup(self):
        """Closes threads and shuts down speech channels."""
        self.is_running = False
        self.stop()
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        logger.debug("TTS background speech workers destroyed.")
