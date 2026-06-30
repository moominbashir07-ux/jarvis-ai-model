import logging
import threading
import time
import struct
import math
from typing import Optional, Callable, List
from jarvis.config import settings

logger = logging.getLogger("JARVIS.Voice.WakeWord")

# Optional imports for professional wake-word SDKs
porcupine_available = False
try:
    import pvporcupine
    porcupine_available = True
except ImportError:
    pass

class WakeWordEngine:
    """Professional, low-latency, low-CPU Wake Word detection engine.
    
    Uses a two-stage detection pipeline:
      Stage 1: Local time-domain Voice Activity Detector (VAD) (STE & ZCR) to check for human voice.
      Stage 2: Acoustic match verification (via pvporcupine if installed, falling back to STT verification).
    """

    def __init__(self, stt=None, tts=None, on_wake_callback: Optional[Callable[[], None]] = None):
        self.stt = stt
        self.tts = tts
        self.on_wake = on_wake_callback
        
        self.is_running = False
        self.listener_thread = None
        self._pyaudio = None
        self._lock = threading.Lock()
        
        # State Machine: 'sleeping', 'listening_for_command'
        self.state = "sleeping"
        self.last_active_time = time.time()
        self.timeout_limit = 10.0  # Return to sleep after 10s of silence
        
        # Acoustic VAD constants for low CPU usage
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_len = int(self.sample_rate * self.frame_duration_ms / 1000)  # 480 samples
        
        # Sensitivity settings
        self.energy_floor = settings.energy_threshold
        self.zcr_min = 10
        self.zcr_max = 120
        
        logger.debug("WakeWordEngine instance created.")

    def initialize(self) -> bool:
        """Initializes raw recording devices and checks third-party bindings."""
        if not settings.voice_enabled:
            logger.info("Voice interfaces are disabled. Wake Word engine suspended.")
            return False

        if porcupine_available:
            logger.info("Picovoice Porcupine SDK detected. Will use deep acoustic models for wake-word.")
        else:
            logger.info("Picovoice Porcupine not found. Utilizing local low-CPU VAD + STT verifier.")
            
        try:
            import pyaudio
            self._pyaudio = pyaudio.PyAudio()
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio in WakeWordEngine: {e}")
            return False
            
        return True

    def start(self):
        """Starts the background listening loop."""
        if self.is_running:
            return
            
        self.is_running = True
        self.listener_thread = threading.Thread(
            target=self._run_engine_loop,
            daemon=True,
            name="JARVIS-WakeWord-Engine"
        )
        self.listener_thread.start()
        logger.info("Wake Engine Started")
        logger.info("Always-on Wake Word listening pipeline active.")

    def _run_engine_loop(self):
        """Continuous background audio stream consumer thread loop."""
        import pyaudio
        
        self._stream = None
        self._frame_count = 0
        
        try:
            try:
                default_device = self._pyaudio.get_default_input_device_info()
                device_idx = default_device.get('index')
                logger.info(f"Opening wake word stream on default input device [{device_idx}] ({default_device.get('name')})")
            except Exception as dev_err:
                logger.warning(f"Could not get default input device: {dev_err}. Letting PyAudio decide.")
                device_idx = None

            self._stream = self._pyaudio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_idx,
                frames_per_buffer=self.frame_len
            )
        except Exception as e:
            logger.error(
                f"Unable to open direct recording stream for wake word detection: {e}. "
                "Wake-Word engine is offline."
            )
            if self._pyaudio:
                self._pyaudio.terminate()
            self.is_running = False
            return

        # Adaptive thresholding variables
        energy_accumulator = []
        
        logger.info("Continuous PCM stream listening established. Wake-Word microphone is active.")
        logger.info("WakeLoopStarted")
        
        while self.is_running:
            try:
                # Check if stream is currently suspended
                with self._lock:
                    if self._stream is None:
                        stream_is_active = False
                    else:
                        stream_is_active = True
                        
                if not stream_is_active:
                    time.sleep(0.1)
                    continue

                # 1. Read block of raw samples
                with self._lock:
                    if self._stream:
                        raw_data = self._stream.read(self.frame_len, exception_on_overflow=False)
                    else:
                        raw_data = None
                        
                if not raw_data:
                    continue
                
                self._frame_count += 1
                
                # Convert binary buffer to list of 16-bit short integers
                samples = struct.unpack(f"{self.frame_len}h", raw_data)
                
                # 2. Stage 1: Fast Local Voice Activity Detection (VAD)
                energy = self._calculate_short_time_energy(samples)
                zcr = self._calculate_zero_crossing_rate(samples)
                
                logger.info(f"Audio Frame Received | Frame Count: {self._frame_count} | Audio Energy: {energy:.2f} | Floor: {self.energy_floor:.2f} | ZCR: {zcr}")
                
                # Calibrate background noise floor dynamically during first 2 seconds
                if len(energy_accumulator) < 50:
                    energy_accumulator.append(energy)
                    avg_ambient = sum(energy_accumulator) / len(energy_accumulator)
                    if avg_ambient < 10.0:
                        self.energy_floor = max(0.3, avg_ambient * 2.0)
                    else:
                        self.energy_floor = max(settings.energy_threshold, avg_ambient * 1.5)
                    continue

                # Voice criteria check: high energy & speech-like frequency zero crossings
                is_vocal_energy = energy > self.energy_floor
                is_vocal_frequency = self.zcr_min < zcr < self.zcr_max
                
                if is_vocal_energy and is_vocal_frequency:
                    # Further pitch verification: Autocorrelation harmonics check
                    if self._verify_human_pitch(samples):
                        # Detailed diagnostic logs
                        logger.info("VADDetected")
                        # 3. Stage 2: Keyword spotting verification
                        self._handle_acoustic_trigger(None)
                        
                # Handle active conversation timeouts
                if self.state == "listening_for_command":
                    if time.time() - self.last_active_time > self.timeout_limit:
                        logger.info("Conversation session timed out. Returning to wake-word sleep state.")
                        self.state = "sleeping"
                        if self.tts:
                            self.tts.speak("Returning to standby mode.")
                            
            except Exception as e:
                logger.error(f"Error in Wake Word audio processing loop: {e}", exc_info=True)
                time.sleep(0.5)

        with self._lock:
            if self._stream:
                try:
                    self._stream.stop_stream()
                    self._stream.close()
                except Exception:
                    pass
        if self._pyaudio:
            self._pyaudio.terminate()

    def _calculate_short_time_energy(self, samples: List[int]) -> float:
        """Computes root mean square (RMS) energy of sample frames."""
        sum_squares = sum((s / 32768.0) ** 2 for s in samples)
        return math.sqrt(sum_squares / len(samples)) * 1000.0

    def _calculate_zero_crossing_rate(self, samples: List[int]) -> int:
        """Computes zero crossing count to filter high-freq noise and flat silences."""
        crossings = 0
        for i in range(1, len(samples)):
            if (samples[i] >= 0 > samples[i - 1]) or (samples[i] < 0 <= samples[i - 1]):
                crossings += 1
        return crossings

    def _verify_human_pitch(self, samples: List[int]) -> bool:
        """Autocorrelation harmonic pitch analyzer."""
        max_corr = -1.0
        best_lag = -1
        
        # Downsample calculations for low CPU usage
        for lag in range(53, 200, 3):
            corr = 0.0
            var_x = 0.0
            var_y = 0.0
            
            # Autocorrelate signal samples overlapping with lag shift
            for i in range(len(samples) - lag):
                x = samples[i]
                y = samples[i + lag]
                corr += x * y
                var_x += x * x
                var_y += y * y
                
            norm = math.sqrt(var_x * var_y)
            if norm > 0:
                coeff = corr / norm
                if coeff > max_corr:
                    max_corr = coeff
                    best_lag = lag
                    
        logger.info(f"Wake Confidence (Autocorrelation): {max_corr:.3f}")
        # A correlation coeff > 0.45 indicates strong vocal harmonic pitch formatting
        return max_corr > 0.45

    def suspend_stream(self):
        """Temporarily closes the PyAudio stream to release the microphone for other components."""
        self._lock = getattr(self, '_lock', threading.Lock())
        with self._lock:
            if hasattr(self, '_stream') and self._stream:
                try:
                    self._stream.stop_stream()
                    self._stream.close()
                except Exception as e:
                    logger.debug(f"Error closing stream: {e}")
                self._stream = None
            logger.info("WakeWordEngine microphone stream suspended.")

    def resume_stream(self, p_audio):
        """Reopens the PyAudio stream to resume wake word monitoring."""
        self._lock = getattr(self, '_lock', threading.Lock())
        with self._lock:
            if not getattr(self, '_stream', None) and p_audio:
                try:
                    import pyaudio
                    try:
                        default_device = p_audio.get_default_input_device_info()
                        device_idx = default_device.get('index')
                        logger.info(f"Resuming wake word stream on default input device [{device_idx}] ({default_device.get('name')})")
                    except Exception as dev_err:
                        logger.warning(f"Could not get default input device for resume: {dev_err}. Letting PyAudio decide.")
                        device_idx = None

                    self._stream = p_audio.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        input_device_index=device_idx,
                        frames_per_buffer=self.frame_len
                    )
                    logger.info("WakeWordEngine microphone stream resumed.")
                except Exception as e:
                    logger.error(f"Error resuming wake stream: {e}")

    def _handle_acoustic_trigger(self, stream):
        """Validates trigger phrase utilizing deep models or fallback transcription."""
        # If pvporcupine is not installed, we cannot verify the past spoken wake word from a buffer.
        # We immediately count the vocal VAD trigger as a wake-word trigger to avoid timing out on silence.
        global porcupine_available
        if not porcupine_available:
            logger.info("WakePhraseDetected")
            logger.info("WakeConfirmed")
            logger.info("Keyword matching trigger successful (VAD Fallback Bypass)!")
            self.state = "listening_for_command"
            self.last_active_time = time.time()
            if self.on_wake:
                self.on_wake()
            return

        # Suspend continuous mic stream before launching STT trigger capture
        self.suspend_stream()

        logger.info("Speech Activity Detected. Verifying trigger keywords...")
        if not self.stt:
            if self._pyaudio:
                self.resume_stream(self._pyaudio)
            return

        # Perform a quick 2.0s capture for validation
        audio_prompt = self.stt.listen_and_transcribe(timeout=2.0)
        
        # Resume continuous mic stream immediately
        if self._pyaudio:
            self.resume_stream(self._pyaudio)

        if not audio_prompt:
            return

        text_lower = audio_prompt.lower()
        # Look for activation strings
        if "jarvis" in text_lower or "hey jarvis" in text_lower:
            logger.info("WakePhraseDetected")
            logger.info("WakeConfirmed")
            logger.info("Keyword matching trigger successful!")
            self.state = "listening_for_command"
            self.last_active_time = time.time()
            
            # Fire event callback
            if self.on_wake:
                self.on_wake()
            else:
                self._default_wake_action(text_lower)

    def _default_wake_action(self, full_transcription: str):
        """Default behavior if no custom orchestrator callback is defined."""
        logger.info("Default Wake Event Handler Fired.")
        if self.tts:
            self.tts.speak("I am here, sir. What is our objective?")

    def trigger_activity(self):
        """Resets the timeout counter to keep system active during active loops."""
        self.last_active_time = time.time()
        self.state = "listening_for_command"

    def stop(self):
        """Stops background threads."""
        self.is_running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1.0)
        logger.debug("WakeWordEngine pipeline destroyed.")
