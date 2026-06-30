import sys
import time
import logging
import io
from jarvis.config import settings
from jarvis.core.event_bus import EventBus
from jarvis.core.orchestrator import Orchestrator

# Capture logs programmatically
log_capture_string = io.StringIO()
ch = logging.StreamHandler(log_capture_string)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
ch.setFormatter(formatter)

# Root logger setup
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(ch)

# Script console logger
console_logger = logging.getLogger("ScenarioRunner")
console_ch = logging.StreamHandler(sys.stdout)
console_ch.setLevel(logging.INFO)
console_ch.setFormatter(logging.Formatter('%(message)s'))
console_logger.addHandler(console_ch)
console_logger.setLevel(logging.INFO)

def get_new_logs():
    log_contents = log_capture_string.getvalue()
    log_capture_string.truncate(0)
    log_capture_string.seek(0)
    return log_contents

def main():
    console_logger.info("=========================================")
    console_logger.info("    JARVIS SCENARIO VERIFICATION AUDIT   ")
    console_logger.info("=========================================")

    # Initialize Orchestrator
    console_logger.info("[BOOT] Initializing JARVIS Orchestrator...")
    orchestrator = Orchestrator()
    orchestrator.initialize()
    
    # Track events on EventBus
    events_logged = []
    def event_logger(event_type, payload):
        events_logged.append({
            "event": event_type,
            "payload": payload or {},
            "timestamp": time.perf_counter(),
            "wall_time": time.strftime('%H:%M:%S')
        })
    orchestrator.event_bus.subscribe("*", event_logger)
    
    # Flush bootstrap logs
    bootstrap_logs = get_new_logs()
    
    # ----------------- SCENARIO 1 -----------------
    console_logger.info("\n--- EXECUTING SCENARIO 1: 'Hey Jarvis' Wake Trigger ---")
    events_logged.clear()
    get_new_logs() # Clear log buffer
    
    # Mock STT to return None (no command) to test pure wake trigger
    original_stt_listen = orchestrator.stt.listen_and_transcribe
    orchestrator.stt.listen_and_transcribe = lambda timeout=None: None
    
    s1_start = time.perf_counter()
    orchestrator._handle_wake_word_trigger()
    s1_duration = time.perf_counter() - s1_start
    
    # Retrieve Scenario 1 logs
    s1_logs = get_new_logs()
    s1_events = list(events_logged)
    
    # Extract latencies for Scenario 1
    wake_event = next((e for e in s1_events if e["event"] == "WakeDetected"), None)
    speak_start = next((e for e in s1_events if e["event"] == "SpeakingStarted"), None)
    speak_stop = next((e for e in s1_events if e["event"] == "SpeakingStopped"), None)
    listen_start = next((e for e in s1_events if e["event"] == "ListeningStarted"), None)
    
    wake_latency = (speak_start["timestamp"] - wake_event["timestamp"]) if (wake_event and speak_start) else 0.0
    tts_latency = (speak_stop["timestamp"] - speak_start["timestamp"]) if (speak_start and speak_stop) else 0.0
    
    console_logger.info(f"Wake Latency: {wake_latency:.3f}s")
    console_logger.info(f"Greeting TTS Duration: {tts_latency:.3f}s")

    # ----------------- SCENARIO 2 -----------------
    console_logger.info("\n--- EXECUTING SCENARIO 2: 'Hey Jarvis open settings' ---")
    events_logged.clear()
    get_new_logs()
    
    # Mock STT to return "open settings"
    orchestrator.stt.listen_and_transcribe = lambda timeout=None: "open settings"
    
    s2_start = time.perf_counter()
    orchestrator._handle_wake_word_trigger()
    
    # Wait for the background command processing thread to finish speaking
    time.sleep(2.0)
    s2_duration = time.perf_counter() - s2_start
    
    s2_logs = get_new_logs()
    s2_events = list(events_logged)
    
    # Extract latencies for Scenario 2
    listening_start_ev = next((e for e in s2_events if e["event"] == "ListeningStarted"), None)
    listening_stop_ev = next((e for e in s2_events if e["event"] == "ListeningStopped"), None)
    response_ev = next((e for e in s2_events if e["event"] == "ResponseComplete"), None)
    tts_start_ev = next((e for e in s2_events if e["event"] == "SpeakingStarted" and "Settings" in e["payload"].get("response", "")), None)
    tts_stop_ev = next((e for e in s2_events if e["event"] == "SpeakingStopped" and "Settings" in e["payload"].get("response", "")), None)
    
    stt_latency = (listening_stop_ev["timestamp"] - listening_start_ev["timestamp"]) if (listening_start_ev and listening_stop_ev) else 0.0
    cmd_latency = (response_ev["timestamp"] - listening_stop_ev["timestamp"]) if (response_ev and listening_stop_ev) else 0.0
    tts_feedback_latency = (tts_stop_ev["timestamp"] - tts_start_ev["timestamp"]) if (tts_start_ev and tts_stop_ev) else 0.0
    
    console_logger.info(f"STT Latency: {stt_latency:.3f}s")
    console_logger.info(f"Command Registry Match & Exec Latency: {cmd_latency:.3f}s")
    console_logger.info(f"Feedback TTS Duration: {tts_feedback_latency:.3f}s")

    # ----------------- SCENARIO 3 -----------------
    console_logger.info("\n--- EXECUTING SCENARIO 3: 'Hey Jarvis open calculator' ---")
    events_logged.clear()
    get_new_logs()
    
    orchestrator.stt.listen_and_transcribe = lambda timeout=None: "open calculator"
    
    s3_start = time.perf_counter()
    orchestrator._handle_wake_word_trigger()
    time.sleep(2.0)
    s3_duration = time.perf_counter() - s3_start
    
    s3_logs = get_new_logs()
    s3_events = list(events_logged)

    # ----------------- SCENARIO 4 -----------------
    console_logger.info("\n--- EXECUTING SCENARIO 4: 'Hey Jarvis what time is it' ---")
    events_logged.clear()
    get_new_logs()
    
    orchestrator.stt.listen_and_transcribe = lambda timeout=None: "what time is it"
    
    s4_start = time.perf_counter()
    orchestrator._handle_wake_word_trigger()
    time.sleep(2.5) # Wait for LLM routing and SAPI5 speaking
    s4_duration = time.perf_counter() - s4_start
    
    s4_logs = get_new_logs()
    s4_events = list(events_logged)
    
    # Extract latencies for Scenario 4
    thinking_start_ev = next((e for e in s4_events if e["event"] == "ThinkingStarted"), None)
    thinking_stop_ev = next((e for e in s4_events if e["event"] == "ThinkingStopped"), None)
    provider_latency = (thinking_stop_ev["timestamp"] - thinking_start_ev["timestamp"]) if (thinking_start_ev and thinking_stop_ev) else 0.0
    console_logger.info(f"Provider Router & LLM Latency: {provider_latency:.3f}s")

    # ----------------- SCENARIO 5 -----------------
    console_logger.info("\n--- EXECUTING SCENARIO 5: 'Hey Jarvis search Google for latest AI news' ---")
    events_logged.clear()
    get_new_logs()
    
    orchestrator.stt.listen_and_transcribe = lambda timeout=None: "search Google for latest AI news"
    
    s5_start = time.perf_counter()
    orchestrator._handle_wake_word_trigger()
    time.sleep(2.0)
    s5_duration = time.perf_counter() - s5_start
    
    s5_logs = get_new_logs()
    s5_events = list(events_logged)

    # Clean shutdown
    orchestrator.stt.listen_and_transcribe = original_stt_listen
    orchestrator.shutdown()
    
    # Output Scenario Details
    print("\n" + "="*50)
    print("                SCENARIO LOG EVIDENCE")
    print("="*50)
    
    print("\n[BOOTSTRAP LOGS]")
    print(bootstrap_logs)
    
    print("\n[SCENARIO 1: Hey Jarvis]")
    print("EVENTS:")
    for ev in s1_events:
        print(f"  - {ev['wall_time']} | Event: {ev['event']} | Payload: {ev['payload']}")
    print("LOGS:")
    print(s1_logs)
    
    print("\n[SCENARIO 2: Open Settings]")
    print("EVENTS:")
    for ev in s2_events:
        print(f"  - {ev['wall_time']} | Event: {ev['event']} | Payload: {ev['payload']}")
    print("LOGS:")
    print(s2_logs)
    
    print("\n[SCENARIO 3: Open Calculator]")
    print("EVENTS:")
    for ev in s3_events:
        print(f"  - {ev['wall_time']} | Event: {ev['event']} | Payload: {ev['payload']}")
    print("LOGS:")
    print(s3_logs)
    
    print("\n[SCENARIO 4: What time is it]")
    print("EVENTS:")
    for ev in s4_events:
        print(f"  - {ev['wall_time']} | Event: {ev['event']} | Payload: {ev['payload']}")
    print("LOGS:")
    print(s4_logs)
    
    print("\n[SCENARIO 5: Search Google for latest AI news]")
    print("EVENTS:")
    for ev in s5_events:
        print(f"  - {ev['wall_time']} | Event: {ev['event']} | Payload: {ev['payload']}")
    print("LOGS:")
    print(s5_logs)

    # Write logs to workspace for audit review
    try:
        with open("logs/scenarios_audit_run.log", "w", encoding="utf-8") as f:
            f.write(f"Scenario 1 Latencies:\n  Wake Latency: {wake_latency:.3f}s\n  Greeting TTS: {tts_latency:.3f}s\n\n")
            f.write(f"Scenario 2 Latencies:\n  STT Latency: {stt_latency:.3f}s\n  Cmd Registry Latency: {cmd_latency:.3f}s\n  Feedback TTS: {tts_feedback_latency:.3f}s\n\n")
            f.write(f"Scenario 4 Latencies:\n  Provider Latency: {provider_latency:.3f}s\n\n")
            f.write(f"S1 Logs:\n{s1_logs}\n\nS2 Logs:\n{s2_logs}\n\nS3 Logs:\n{s3_logs}\n\nS4 Logs:\n{s4_logs}\n\nS5 Logs:\n{s5_logs}\n")
    except Exception as e:
        pass

if __name__ == "__main__":
    main()
