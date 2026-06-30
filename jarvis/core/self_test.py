import logging
import threading
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Core.SelfTest")

class SystemSelfTestManager:
    """Manages the startup diagnostic self-tests verifying system components."""

    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.report = {}
        self.overall_status = "PASS"

    def run_all_tests(self) -> Dict[str, str]:
        """Runs the self-tests for all core system services."""
        logger.info("Executing JARVIS diagnostic self-tests...")
        
        self.report["microphone"] = self._test_microphone()
        self.report["speaker"] = self._test_speaker()
        self.report["tts"] = self._test_tts()
        self.report["stt"] = self._test_stt()
        self.report["ipc"] = self._test_ipc()
        self.report["event_bus"] = self._test_event_bus()
        self.report["ai_providers"] = self._test_ai_providers()
        self.report["automation"] = self._test_automation()
        
        # Calculate overall status
        status_vals = list(self.report.values())
        if "FAIL" in status_vals:
            self.overall_status = "FAIL"
        elif "WARNING" in status_vals:
            self.overall_status = "WARNING"
        else:
            self.overall_status = "PASS"
            
        logger.info(f"Self-tests complete. Overall diagnostic status: {self.overall_status}")
        logger.debug(f"Self-test report details: {self.report}")
        
        # Publish diagnostic report to EventBus
        if self.orch and self.orch.event_bus:
            self.orch.event_bus.publish("SelfTestReport", {
                "overall": self.overall_status,
                "details": self.report
            })
            
        return self.report

    def _test_microphone(self) -> str:
        try:
            # If listener is running and has stream, microphone is already verified
            if self.orch and self.orch.listener and getattr(self.orch.listener, 'is_running', False):
                if getattr(self.orch.listener, '_stream', None) is not None:
                    return "PASS"
                p = getattr(self.orch.listener, '_pyaudio', None)
                if p:
                    info = p.get_default_input_device_info()
                    if info:
                        return "PASS"
            
            import pyaudio
            p = pyaudio.PyAudio()
            info = p.get_default_input_device_info()
            p.terminate()
            if info:
                return "PASS"
            return "WARNING"
        except Exception:
            return "FAIL"

    def _test_speaker(self) -> str:
        try:
            if self.orch and self.orch.listener and getattr(self.orch.listener, 'is_running', False):
                p = getattr(self.orch.listener, '_pyaudio', None)
                if p:
                    info = p.get_default_output_device_info()
                    if info:
                        return "PASS"
            
            import pyaudio
            p = pyaudio.PyAudio()
            info = p.get_default_output_device_info()
            p.terminate()
            if info:
                return "PASS"
            return "WARNING"
        except Exception:
            return "FAIL"

    def _test_tts(self) -> str:
        if self.orch and self.orch.tts and self.orch.tts.enabled:
            # We check if worker thread is alive or PyTTSX3 initialized
            if self.orch.tts.worker_thread or self.orch.tts.engine or self.orch.tts.provider == "system":
                return "PASS"
            return "WARNING"
        return "FAIL"

    def _test_stt(self) -> str:
        if self.orch and self.orch.stt and self.orch.stt.enabled:
            if self.orch.stt.recognizer:
                return "PASS"
            return "WARNING"
        return "FAIL"

    def _test_ipc(self) -> str:
        if self.orch and self.orch.ipc and self.orch.ipc.is_running:
            return "PASS"
        return "FAIL"

    def _test_event_bus(self) -> str:
        if not self.orch or not self.orch.event_bus:
            return "FAIL"
        
        # Test event publish/subscribe sanity
        test_success = False
        def test_handler(event_type, payload):
            nonlocal test_success
            if payload.get("check") == "ok":
                test_success = True
                
        self.orch.event_bus.subscribe("SelfTestCheck", test_handler)
        self.orch.event_bus.publish("SelfTestCheck", {"check": "ok"})
        # Clean up subscription
        self.orch.event_bus.unsubscribe("SelfTestCheck", test_handler)
            
        return "PASS" if test_success else "FAIL"

    def _test_ai_providers(self) -> str:
        if self.orch and self.orch.brain and self.orch.brain.router:
            router = self.orch.brain.router
            ollama_health = router.providers.get("ollama")
            if ollama_health and ollama_health.health_status == "ONLINE":
                return "PASS"
            return "WARNING"
        return "FAIL"

    def _test_automation(self) -> str:
        if self.orch and self.orch.automation:
            return "PASS"
        return "FAIL"
