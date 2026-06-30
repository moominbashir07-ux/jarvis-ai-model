import speech_recognition as sr
import sys

def main():
    print("=========================================")
    print("           STANDALONE STT TEST           ")
    print("=========================================")
    
    # 1. Check SpeechRecognition and PyAudio presence
    print(f"SpeechRecognition version: {sr.__version__}")
    
    try:
        import pyaudio
        print(f"PyAudio version: {pyaudio.__version__}")
    except ImportError:
        print("[FAIL] PyAudio is not installed.")
        sys.exit(1)

    # 2. Check microphone
    try:
        mic = sr.Microphone()
        print("[PASS] Microphone object created successfully.")
    except Exception as e:
        print(f"[FAIL] Unable to create Microphone: {e}")
        sys.exit(1)

    # 3. Create Recognizer
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    # 4. Calibrate and record
    try:
        with mic as source:
            print("\n[INFO] Calibrating ambient noise (please remain silent)...")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print(f"[INFO] Calibrated energy threshold: {recognizer.energy_threshold:.2f}")
            
            print("\n[Speak now] (recording for up to 5 seconds)...")
            audio = recognizer.listen(source, timeout=5.0, phrase_time_limit=5.0)
            print("[INFO] Audio captured. Processing transcription...")
            
    except sr.WaitTimeoutError:
        print("[FAIL] Speech listener timed out waiting for audio.")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Error during audio recording: {e}")
        sys.exit(1)

    # 5. Transcribe
    try:
        print("[INFO] Querying Google Speech Recognition free tier...")
        text = recognizer.recognize_google(audio)
        print(f"\n[PASS] Transcription successful!")
        print(f"Transcript: '{text}'")
    except sr.UnknownValueError:
        print("\n[FAIL] Google Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"\n[FAIL] Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"\n[FAIL] Unhandled error during transcription: {e}")

if __name__ == "__main__":
    main()
