import sys
import time
import logging
from jarvis.config import settings
from jarvis.core.event_bus import EventBus
from jarvis.core.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
logger = logging.getLogger("VerifyVoicePipeline")

def main():
    print("=========================================")
    print("       JARVIS E2E VOICE PIPELINE TEST    ")
    print("=========================================")

    # 1. Initialize Orchestrator
    logger.info("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    orchestrator.initialize()
    
    # 2. Track events published to the EventBus
    events_logged = []
    def event_logger(event_type, payload):
        logger.info(f"[EVENT_BUS] Event published: '{event_type}' with payload: {payload}")
        events_logged.append((event_type, payload))
        
    orchestrator.event_bus.subscribe("*", event_logger)

    # 3. Mock the STT recognition to return "open settings"
    # This simulates the user saying "open settings" when JARVIS starts listening
    original_stt_listen = orchestrator.stt.listen_and_transcribe
    
    def mock_listen_and_transcribe(timeout=None):
        logger.info("STT: Mocking voice input capture: 'open settings'")
        return "open settings"
        
    orchestrator.stt.listen_and_transcribe = mock_listen_and_transcribe

    # 4. Trigger the wake word callback directly to initiate the flow
    logger.info("Simulating wake phrase detection (Hey Jarvis)...")
    # This runs the greeting, plays TTS, and launches STT listen
    orchestrator._handle_wake_word_trigger()
    
    # 5. Wait for background thread processing to complete (LLM router & command execution)
    logger.info("Awaiting async command execution and speech synthesis output...")
    start_wait = time.time()
    success = False
    
    # Wait for up to 10 seconds
    while time.time() - start_wait < 10.0:
        event_types = [ev[0] for ev in events_logged]
        if "ResponseComplete" in event_types and "SpeakingStopped" in event_types:
            success = True
            break
        time.sleep(0.1)

    # 6. Cleanup
    logger.info("Shutting down orchestrator...")
    orchestrator.stt.listen_and_transcribe = original_stt_listen
    orchestrator.shutdown()

    # 7. Print diagnostic checklist report
    print("\n=========================================")
    print("           TRANSITION VERIFICATION       ")
    print("=========================================")
    
    checklist = {
        "WakeDetected": False,
        "SpeakingStarted (Greeting)": False,
        "SpeakingStopped (Greeting)": False,
        "ListeningStarted": False,
        "ListeningStopped": False,
        "ThinkingStarted": False,
        "ThinkingStopped": False,
        "ResponseComplete": False,
        "SpeakingStarted (Action Feedback)": False,
        "SpeakingStopped (Action Feedback)": False
    }

    speaking_count = 0
    for ev_type, payload in events_logged:
        if ev_type == "WakeDetected":
            checklist["WakeDetected"] = True
        elif ev_type == "ListeningStarted":
            checklist["ListeningStarted"] = True
        elif ev_type == "ListeningStopped":
            checklist["ListeningStopped"] = True
        elif ev_type == "ThinkingStarted":
            checklist["ThinkingStarted"] = True
        elif ev_type == "ThinkingStopped":
            checklist["ThinkingStopped"] = True
        elif ev_type == "ResponseComplete":
            checklist["ResponseComplete"] = True
            print(f"[PASS] ResponseComplete content: '{payload.get('response')}'")
        elif ev_type == "SpeakingStarted":
            speaking_count += 1
            if speaking_count == 1:
                checklist["SpeakingStarted (Greeting)"] = True
            else:
                checklist["SpeakingStarted (Action Feedback)"] = True
        elif ev_type == "SpeakingStopped":
            if checklist["SpeakingStarted (Action Feedback)"]:
                checklist["SpeakingStopped (Action Feedback)"] = True
            else:
                checklist["SpeakingStopped (Greeting)"] = True

    all_passed = True
    for transition, status in checklist.items():
        status_str = "PASS" if status else "FAIL"
        print(f"{transition:<40} : {status_str}")
        if not status:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] E2E Voice-to-Action pipeline is fully operational!")
        sys.exit(0)
    else:
        print("\n[FAIL] E2E Voice-to-Action pipeline has missing or broken transitions.")
        sys.exit(1)

if __name__ == "__main__":
    main()
