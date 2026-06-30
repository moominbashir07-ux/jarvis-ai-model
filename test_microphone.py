import pyaudio
import wave
import sys
import math
import struct
from pathlib import Path

def list_devices():
    p = pyaudio.PyAudio()
    print("=========================================")
    print("        AVAILABLE AUDIO DEVICES          ")
    print("=========================================")
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    default_input = p.get_default_input_device_info()
    print(f"Default Input Device Index: {default_input.get('index')} - {default_input.get('name')}\n")

    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            print(f"Device [{i}]: {device_info.get('name')}")
            print(f"   Max Input Channels: {device_info.get('maxInputChannels')}")
            print(f"   Default Sample Rate: {device_info.get('defaultSampleRate')}")
            print("-----------------------------------------")
    p.terminate()

def record_audio(duration_sec=5, sample_rate=16000):
    p = pyaudio.PyAudio()
    
    try:
        default_device = p.get_default_input_device_info()
    except IOError as e:
        print(f"[FAIL] Unable to get default input device info: {e}")
        p.terminate()
        return False
        
    device_idx = default_device.get('index')
    channels = 1
    chunk_size = 512
    
    print(f"\n[INFO] Attempting to open recording stream on device [{device_idx}] ({default_device.get('name')})...")
    
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device_idx,
            frames_per_buffer=chunk_size
        )
    except Exception as e:
        print(f"[FAIL] Failed to open recording stream: {e}")
        p.terminate()
        return False
        
    print(f"[INFO] Stream open successful. Recording for {duration_sec} seconds...")
    frames = []
    energy_sum = 0
    sample_count = 0
    
    # Read chunk loop
    for _ in range(0, int(sample_rate / chunk_size * duration_sec)):
        try:
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate short-time RMS energy of the chunk
            shorts = struct.unpack(f"{chunk_size}h", data)
            for s in shorts:
                energy_sum += (s / 32768.0) ** 2
                sample_count += 1
        except Exception as e:
            print(f"[WARNING] Error reading chunk frame: {e}")
            
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Calculate overall RMS energy
    if sample_count > 0:
        rms = math.sqrt(energy_sum / sample_count) * 1000.0
    else:
        rms = 0.0
        
    print(f"[INFO] Recording complete. Signal RMS Energy: {rms:.3f}")
    
    # Save to WAV
    output_dir = Path("logs")
    output_dir.mkdir(exist_ok=True)
    wav_path = output_dir / "microphone_test.wav"
    
    try:
        wf = wave.open(str(wav_path), 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"[PASS] Saved test audio file to: {wav_path.resolve()}")
    except Exception as e:
        print(f"[FAIL] Unable to save WAV file: {e}")
        return False
        
    # Evaluate energy threshold
    if rms > 1.0:
        print(f"[PASS] Audio energy verified ({rms:.3f} > 1.0 threshold). Mic is receiving signal.")
        return True
    else:
        print(f"[WARNING] Extremely low audio energy detected ({rms:.3f} <= 1.0). Microphone may be muted or gains too low.")
        return True

if __name__ == "__main__":
    list_devices()
    record_audio()
