import time
import logging
import sys
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock
from jarvis.core.orchestrator import Orchestrator
from jarvis.config import settings

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (AcceptanceTest) %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("JARVIS.AcceptanceTest")

class AcceptanceTestManager:
    """Automated Acceptance Testing manager validating conversational flows and latency metrics."""

    def __init__(self):
        self.orchestrator = None
        self.events_received: List[Dict[str, Any]] = []
        self.results: Dict[str, Dict[str, Any]] = {}

    def _event_callback(self, event_type: str, payload: Dict[str, Any] = None):
        self.events_received.append({
            "event": event_type,
            "payload": payload or {},
            "time": time.perf_counter()
        })
        logger.info(f"Test Event Bus captured: {event_type}")

    def setup(self):
        """Initializes orchestrator with mock audio streams to run in headless test environments."""
        logger.info("Setting up acceptance test environment...")
        self.events_received.clear()
        
        # Patch PyAudio, SAPI5, and SpeechRecognition to avoid blocking physical hardware locks during tests
        self.patch_pyaudio = patch('pyaudio.PyAudio')
        self.patch_sr = patch('speech_recognition.Recognizer')
        self.patch_tts = patch('pyttsx3.init')
        
        self.mock_pyaudio = self.patch_pyaudio.start()
        self.mock_sr = self.patch_sr.start()
        self.mock_tts = self.patch_tts.start()
        
        # Setup mock PyTTSX3 engine behavior
        self.mock_engine = MagicMock()
        self.mock_tts.return_value = self.mock_engine
        
        # Configure mock PyAudio instance to return empty byte frames for wake activity monitor
        mock_pyaudio_inst = self.mock_pyaudio.return_value
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'\x00' * 960  # 480 samples * 2 bytes
        mock_pyaudio_inst.open.return_value = mock_stream
        
        # Setup orchestrator
        self.orchestrator = Orchestrator()
        
        # Subscribe wildcard to track all event notifications
        self.orchestrator.event_bus.subscribe("*", self._event_callback)
        
        # Disable GUI start-up inside orchestrator initialize to keep tests headless
        with patch('jarvis.ui.gui_manager.GuiManager.initialize') as mock_gui_init:
            self.orchestrator.initialize()
            
        # Mock STT to prevent blocking user prompt inputs or CP1252 emoji encoding exceptions
        self.orchestrator.stt.listen_and_transcribe = MagicMock(return_value="hello jarvis")

    def teardown(self):
        """Clean up mocked patches and shut down orchestrator loops."""
        logger.info("Tearing down acceptance test environment...")
        if self.orchestrator:
            self.orchestrator.shutdown()
        
        self.patch_pyaudio.stop()
        self.patch_sr.stop()
        self.patch_tts.stop()

    def run_all_scenarios(self):
        """Runs the complete suite of real-world conversational user scenarios."""
        logger.info("=========================================")
        logger.info("    LAUNCHING JARVIS ACCEPTANCE SUITE    ")
        logger.info("=========================================")
        
        self.setup()
        
        try:
            # 1. Startup Diagnostics Check
            self.scenario_startup_diagnostics()
            
            # 2. Hey Jarvis Wake Verification
            self.scenario_wake_trigger()
            
            # 3. Command Registry Actions: Open Settings
            self.scenario_command_settings()
            
            # 4. Command Registry Actions: Open Calculator
            self.scenario_command_calculator()
            
            # 5. Command Registry Actions: Open Chrome
            self.scenario_command_chrome()
            
            # 6. Command Registry Actions: Search Google
            self.scenario_command_search()
            
            # 7. General Conversation (AI Routing & Streaming)
            self.scenario_general_conversation()
            
            # 8. Speech Interruption check
            self.scenario_speech_interruption()
            
        finally:
            self.teardown()
            
        self.generate_report()

    def scenario_startup_diagnostics(self):
        logger.info("Scenario: Startup Diagnostics validation...")
        start_time = time.perf_counter()
        
        # Diagnostics automatically run on initialize. We check events_received.
        report_event = next((e for e in self.events_received if e["event"] == "SelfTestReport"), None)
        
        if report_event:
            status = report_event["payload"].get("overall")
            details = report_event["payload"].get("details", {})
            latency = time.perf_counter() - start_time
            
            self.results["Startup Diagnostics"] = {
                "status": "PASS" if status in ["PASS", "WARNING"] else "FAIL",
                "details": f"Overall: {status} | Subsystem details: {details}",
                "latency_sec": latency
            }
        else:
            self.results["Startup Diagnostics"] = {
                "status": "FAIL",
                "details": "SelfTestReport event was not published during boot loader sequence.",
                "latency_sec": 0.0
            }

    def scenario_wake_trigger(self):
        logger.info("Scenario: Wake Word trigger activation...")
        
        # Empty logs and trigger wake manually
        self.events_received.clear()
        start_time = time.perf_counter()
        
        # Simulate acoustic hit handler call
        self.orchestrator._handle_wake_word_trigger()
        
        # Wait for background thread to process the confirmation speech queue
        time.sleep(0.3)
        
        # Verify wake transitions
        wake_event = next((e for e in self.events_received if e["event"] == "WakeDetected"), None)
        speak_start = next((e for e in self.events_received if e["event"] == "SpeakingStarted"), None)
        listening_start = next((e for e in self.events_received if e["event"] == "ListeningStarted"), None)
        
        latency = time.perf_counter() - start_time
        
        if wake_event and speak_start and listening_start:
            # Measure time to speak confirmation greeting
            speech_latency = speak_start["time"] - start_time
            self.results["Hey Jarvis Wake Word"] = {
                "status": "PASS",
                "details": f"WakeDetected, SpeakingStarted, and ListeningStarted fired successfully. Speech confirmation delay: {speech_latency:.3f}s",
                "latency_sec": latency
            }
        else:
            self.results["Hey Jarvis Wake Word"] = {
                "status": "FAIL",
                "details": f"Missing events. WakeDetected={bool(wake_event)}, SpeakingStarted={bool(speak_start)}, ListeningStarted={bool(listening_start)}",
                "latency_sec": latency
            }

    def scenario_command_settings(self):
        logger.info("Scenario: Execute Command 'Open settings'...")
        self.events_received.clear()
        start_time = time.perf_counter()
        
        # Mock automation launch_website/open_app to avoid spawning real windows during test
        with patch.object(self.orchestrator.automation, 'open_app', return_value=(True, "OK")) as mock_open:
            response = self.orchestrator.process_input("open settings", source="voice")
            
            # Wait for background queue worker to dispatch SpeakingStarted
            time.sleep(0.3)
            
            # Check execution
            mock_open.assert_called_with("ms-settings:")
            
            # Verify speaking confirm and responses
            response_complete = next((e for e in self.events_received if e["event"] == "ResponseComplete"), None)
            speaking_start = next((e for e in self.events_received if e["event"] == "SpeakingStarted"), None)
            
            latency = time.perf_counter() - start_time
            
            if response_complete and speaking_start and "settings" in response.lower():
                self.results["Command: Open Settings"] = {
                    "status": "PASS",
                    "details": f"Spoken feedback: '{response}'. CommandRegistry routed instantly.",
                    "latency_sec": latency
                }
            else:
                self.results["Command: Open Settings"] = {
                    "status": "FAIL",
                    "details": "Command not routed correctly or speaking events missed.",
                    "latency_sec": latency
                }

    def scenario_command_calculator(self):
        logger.info("Scenario: Execute Command 'Open calculator'...")
        self.events_received.clear()
        start_time = time.perf_counter()
        
        with patch.object(self.orchestrator.automation, 'open_app', return_value=(True, "OK")) as mock_open:
            response = self.orchestrator.process_input("open calculator", source="voice")
            mock_open.assert_called_with("calc.exe")
            
            response_complete = next((e for e in self.events_received if e["event"] == "ResponseComplete"), None)
            latency = time.perf_counter() - start_time
            
            if response_complete and "calculator" in response.lower():
                self.results["Command: Open Calculator"] = {
                    "status": "PASS",
                    "details": f"Spoken feedback: '{response}'",
                    "latency_sec": latency
                }
            else:
                self.results["Command: Open Calculator"] = {
                    "status": "FAIL",
                    "details": "Command failed to launch calc.exe preset.",
                    "latency_sec": latency
                }

    def scenario_command_chrome(self):
        logger.info("Scenario: Execute Command 'Open chrome'...")
        self.events_received.clear()
        start_time = time.perf_counter()
        
        with patch.object(self.orchestrator.automation, 'open_app', return_value=(True, "OK")) as mock_open:
            response = self.orchestrator.process_input("open chrome", source="voice")
            mock_open.assert_called_with("chrome.exe")
            
            response_complete = next((e for e in self.events_received if e["event"] == "ResponseComplete"), None)
            latency = time.perf_counter() - start_time
            
            if response_complete and "chrome" in response.lower():
                self.results["Command: Open Chrome"] = {
                    "status": "PASS",
                    "details": f"Spoken feedback: '{response}'",
                    "latency_sec": latency
                }
            else:
                self.results["Command: Open Chrome"] = {
                    "status": "FAIL",
                    "details": "Command failed to launch chrome.exe preset.",
                    "latency_sec": latency
                }

    def scenario_command_search(self):
        logger.info("Scenario: Execute Command 'Search Google'...")
        self.events_received.clear()
        start_time = time.perf_counter()
        
        with patch.object(self.orchestrator.automation, 'launch_website', return_value=(True, "OK")) as mock_launch:
            response = self.orchestrator.process_input("search google for artificial intelligence", source="voice")
            
            # Check URL structure
            mock_launch.assert_called()
            call_url = mock_launch.call_args[0][0]
            
            latency = time.perf_counter() - start_time
            
            if "google.com/search" in call_url and "searching google for" in response.lower():
                self.results["Command: Search Google"] = {
                    "status": "PASS",
                    "details": f"Extracted search URL: '{call_url}' | Spoken: '{response}'",
                    "latency_sec": latency
                }
            else:
                self.results["Command: Search Google"] = {
                    "status": "FAIL",
                    "details": f"Query extraction failed. Extracted URL: {call_url}",
                    "latency_sec": latency
                }

    def scenario_general_conversation(self):
        logger.info("Scenario: General Conversation (Brain Stream verification)...")
        self.events_received.clear()
        start_time = time.perf_counter()
        
        # Test routing and token generation chunks
        response = self.orchestrator.process_input("What is the speed of light?", source="voice")
        
        # Verify event stream
        thinking_start = next((e for e in self.events_received if e["event"] == "ThinkingStarted"), None)
        token_chunks = [e for e in self.events_received if e["event"] == "TokenChunk"]
        thinking_stop = next((e for e in self.events_received if e["event"] == "ThinkingStopped"), None)
        response_complete = next((e for e in self.events_received if e["event"] == "ResponseComplete"), None)
        
        latency = time.perf_counter() - start_time
        
        if thinking_start and len(token_chunks) > 0 and thinking_stop and response_complete:
            self.results["General Conversation Router"] = {
                "status": "PASS",
                "details": f"Routed successfully. ThinkingStarted/Stopped bounds verified. Chunks captured: {len(token_chunks)}",
                "latency_sec": latency
            }
        else:
            self.results["General Conversation Router"] = {
                "status": "FAIL",
                "details": f"Stream events failed. Token chunks: {len(token_chunks)} | Response complete: {bool(response_complete)}",
                "latency_sec": latency
            }

    def scenario_speech_interruption(self):
        logger.info("Scenario: Speech Interruption checks...")
        self.events_received.clear()
        start_time = time.perf_counter()
        
        # Simulate pushing speech output and requesting an immediate stop interrupt
        self.orchestrator.tts.speak("Engaging core backup drives. Warming up system thrusters.")
        
        # Trigger immediate interrupt stop
        self.orchestrator.tts.stop()
        
        latency = time.perf_counter() - start_time
        
        if not self.orchestrator.tts.is_speaking:
            self.results["Speech Interruption Logic"] = {
                "status": "PASS",
                "details": "tts.stop() successfully reset the speech queue and flag to standby.",
                "latency_sec": latency
            }
        else:
            self.results["Speech Interruption Logic"] = {
                "status": "FAIL",
                "details": "Speech output flag remained locked as speaking.",
                "latency_sec": latency
            }

    def generate_report(self):
        """Prints a clean status report detailing latencies and passes."""
        logger.info("\n")
        logger.info("=========================================")
        logger.info("   JARVIS AI OS: ACCEPTANCE TEST REPORT  ")
        logger.info("=========================================")
        logger.info(f"Test Run Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Target Environment: {settings.env.upper()}")
        logger.info("-----------------------------------------")
        
        passed_tests = 0
        total_tests = len(self.results)
        
        for name, data in self.results.items():
            status_indicator = "[PASS]" if data["status"] == "PASS" else "[FAIL]"
            logger.info(f"{status_indicator} {name}")
            logger.info(f"        Latency: {data['latency_sec']:.3f} seconds")
            logger.info(f"        Evidence: {data['details']}")
            logger.info("-----------------------------------------")
            
            if data["status"] == "PASS":
                passed_tests += 1
                
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        logger.info(f"SUMMARY: Passed {passed_tests} / {total_tests} scenarios ({success_rate:.1f}% Success)")
        logger.info("=========================================\n")
        
        # Save to artifacts directory
        try:
            report_file = settings.root_dir / "logs" / "acceptance_test_report.log"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("=========================================\n")
                f.write("   JARVIS AI OS: ACCEPTANCE TEST REPORT  \n")
                f.write("=========================================\n")
                for name, data in self.results.items():
                    f.write(f"[{data['status']}] {name}\n")
                    f.write(f"    Latency: {data['latency_sec']:.3f}s\n")
                    f.write(f"    Evidence: {data['details']}\n")
                    f.write("-----------------------------------------\n")
                f.write(f"SUMMARY: Passed {passed_tests} / {total_tests} scenarios ({success_rate:.1f}% Success)\n")
            logger.info(f"Acceptance test log generated at: {report_file}")
        except Exception as e:
            logger.error(f"Failed to write acceptance report file: {e}")

if __name__ == "__main__":
    manager = AcceptanceTestManager()
    manager.run_all_scenarios()
