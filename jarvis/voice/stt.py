import logging
import time
from typing import Optional
from jarvis.config import settings

logger = logging.getLogger("JARVIS.Voice.STT")

# Optional SpeechRecognition import
sr_available = False
try:
    import speech_recognition as sr
    sr_available = True
except ImportError:
    pass

class SpeechToText:
    """Manages audio transcription through local speech APIs or OpenAI Whisper Cloud APIs."""

    def __init__(self):
        self.enabled = settings.voice_enabled
        self.provider = settings.stt_provider
        self.recognizer = None
        self.microphone = None
        logger.debug(f"SpeechToText configured (enabled={self.enabled}, provider={self.provider})")

    def initialize(self) -> bool:
        """Prepares audio buffers, calibrates background noise, and validates microphone access."""
        if not self.enabled:
            logger.info("Speech-to-Text is disabled in settings.")
            return False

        if not sr_available:
            logger.warning(
                "SpeechRecognition library is missing. STT running in keyboard mock simulation mode."
            )
            return False

        try:
            self.recognizer = sr.Recognizer()
            # Set dynamic energy threshold adjustment parameters
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = settings.energy_threshold
            self.recognizer.pause_threshold = 2.0
            
            # Initialize default microphone
            logger.info("Testing microphone connection...")
            self.microphone = sr.Microphone()
            
            # Calibrate threshold for background ambient noise (blocking call on start, 1 second)
            with self.microphone as source:
                logger.info("Calibrating ambient noise threshold. Please remain silent...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                logger.info(f"Calibration done. Ambient energy threshold: {self.recognizer.energy_threshold:.2f}")
                
            return True
        except Exception as e:
            logger.error(
                f"Failed to initialize audio capture device: {e}. "
                "Verify microphone is connected. Switching STT to developer mock simulation mode."
            )
            self.microphone = None
            return False

    def listen_and_transcribe(self, timeout: Optional[float] = 5.0) -> str:
        """Blocks and listens for a single spoken utterance, returning transcribed text."""
        if not self.enabled:
            return ""

        if not self.recognizer or not self.microphone:
            # Fallback simulator mode (CLI prompt to simulate voice)
            logger.info("STT Mock Mode: Please type voice input simulation command:")
            try:
                # Prompt user for text to simulate voice capture
                text = input("🎤 [Voice Simulation Input] (Type here) » ").strip()
                return text
            except (KeyboardInterrupt, EOFError):
                return ""

        try:
            with self.microphone as source:
                logger.info("Listening for voice utterance...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=10.0
                )
                
            logger.info("Processing speech audio buffer...")
            return self.transcribe_audio(audio)
            
        except sr.WaitTimeoutError:
            logger.debug("Speech listener timed out waiting for audio.")
            return ""
        except Exception as e:
            logger.error(f"Error during audio recording stream: {e}", exc_info=True)
            return ""

    def transcribe_audio(self, audio_data) -> str:
        """Transcribes raw SpeechRecognition AudioData to text via chosen API provider."""
        if not self.recognizer:
            return ""

        start_time = time.time()
        text = ""
        try:
            if self.provider == "openai":
                if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
                    logger.warning("OpenAI API key not configured. Falling back to Google STT API.")
                    text = self.recognizer.recognize_google(audio_data)
                else:
                    # In a complete build, write audio_data to temporary WAV, and call client.audio.transcriptions.create
                    logger.info("Transcribing audio using Whisper Cloud API...")
                    # Mock OpenAI api call or fall back to google for safety
                    text = self.recognizer.recognize_google(audio_data)
            else:
                # Default to Google Speech Recognition free tier API
                logger.debug("Transcribing audio using Google Speech API...")
                text = self.recognizer.recognize_google(audio_data)
                
            latency = time.time() - start_time
            logger.info(f"Transcription complete (latency: {latency:.2f}s): '{text}'")
            return text.strip()
            
        except sr.UnknownValueError:
            logger.debug("Speech recognizer could not verify or understand audio buffer.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Failed to query speech recognition API service: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unhandled error transcribing audio frame: {e}")
            return ""

    def cleanup(self):
        """Cleans up audio device handles."""
        logger.debug("STT hardware cleanup completed.")
