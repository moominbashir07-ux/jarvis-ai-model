import sys
import time
import logging
from jarvis.config import settings
from jarvis.core.event_bus import EventBus
from jarvis.voice.tts import TextToSpeech

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
    print("=========================================")
    print("           STANDALONE TTS TEST           ")
    print("=========================================")

    event_bus = EventBus()
    
    events_received = []
    
    def on_event(event_type, payload):
        print(f"\n[EVENT] Received event '{event_type}' with payload: {payload}")
        events_received.append((event_type, payload))

    event_bus.subscribe("SpeakingStarted", on_event)
    event_bus.subscribe("SpeakingStopped", on_event)

    print(f"[INFO] Initializing TTS with provider: {settings.voice_provider}")
    tts = TextToSpeech(event_bus=event_bus)
    
    success = tts.initialize()
    if not success:
        print("[FAIL] TTS initialization failed.")
        sys.exit(1)
        
    print("[PASS] TTS worker thread started.")
    
    # Wait briefly for worker initialization
    time.sleep(1.0)
    
    # Check if native pyttsx3 engine got loaded and report properties
    if tts.engine:
        try:
            voices = tts.engine.getProperty("voices")
            print(f"[INFO] Native SAPI5 engine loaded successfully. Available voices: {len(voices)}")
            for idx, voice in enumerate(voices):
                print(f"  Voice [{idx}]: ID={voice.id}, Name={voice.name}")
            
            # Show current selected voice
            current_voice = tts.engine.getProperty("voice")
            print(f"[INFO] Current selected voice ID: {current_voice}")
        except Exception as e:
            print(f"[WARNING] Could not read pyttsx3 properties: {e}")
    else:
        print("[WARNING] pyttsx3 engine not initialized (likely running in mock speaker mode).")

    # Queue status before speak
    print(f"[INFO] Initial speak queue size: {tts.speak_queue.qsize()}")

    # Speak
    phrase = "JARVIS speech system test successful."
    print(f"[INFO] Requesting speech: '{phrase}'")
    tts.speak(phrase)
    
    print(f"[INFO] Speak queue size after queuing: {tts.speak_queue.qsize()}")
    
    # Wait for speech to play
    print("[INFO] Waiting for speaking events...")
    start_wait = time.time()
    
    # Wait for up to 8 seconds
    while time.time() - start_wait < 8.0:
        if len(events_received) >= 2:
            break
        time.sleep(0.1)

    print("\n=========================================")
    print("              TEST REPORT                ")
    print("=========================================")
    print(f"Events received: {len(events_received)}")
    for ev_type, pay in events_received:
        print(f"  - {ev_type}: {pay}")
        
    print(f"Final queue state: {tts.speak_queue.qsize()}")
    print(f"TTS is_speaking status: {tts.is_speaking}")
    
    tts.cleanup()
    print("[INFO] TTS cleanup completed.")
    
    if len(events_received) >= 2:
        print("[PASS] TTS system test executed successfully.")
    else:
        print("[FAIL] Did not receive all speaking events. Speech synthesis might have stalled.")
        sys.exit(1)

if __name__ == "__main__":
    main()
