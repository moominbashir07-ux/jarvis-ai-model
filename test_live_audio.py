import pyaudio
import math
import struct
import time
import sys

def main():
    p = pyaudio.PyAudio()
    
    try:
        default_device = p.get_default_input_device_info()
        device_idx = default_device.get('index')
        device_name = default_device.get('name')
    except Exception as e:
        print(f"Error getting default input device: {e}")
        p.terminate()
        sys.exit(1)
        
    print(f"Selected Device Index: {device_idx}")
    print(f"Selected Device Name: {device_name}")
    print("-----------------------------------------")
    print("Listening for audio. Speak into the microphone to see if energy increases.")
    print("Press Ctrl+C to stop.")
    print("-----------------------------------------")

    sample_rate = 16000
    chunk_size = 512
    channels = 1
    
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
        print(f"Failed to open recording stream: {e}")
        p.terminate()
        sys.exit(1)

    last_print = time.time()
    energy_sum = 0
    chunk_count = 0

    try:
        while True:
            try:
                data = stream.read(chunk_size, exception_on_overflow=False)
                if not data:
                    continue
                
                # Convert binary buffer to list of 16-bit short integers
                samples = struct.unpack(f"{chunk_size}h", data)
                
                # Calculate root mean square (RMS) energy
                sum_squares = sum((s / 32768.0) ** 2 for s in samples)
                energy = math.sqrt(sum_squares / len(samples)) * 1000.0
                
                energy_sum += energy
                chunk_count += 1
                
                # Print average energy every 1 second
                now = time.time()
                if now - last_print >= 1.0:
                    avg_energy = energy_sum / chunk_count if chunk_count > 0 else 0.0
                    print(f"Energy: {avg_energy:.2f}")
                    sys.stdout.flush()
                    energy_sum = 0
                    chunk_count = 0
                    last_print = now
                    
            except Exception as e:
                print(f"Error reading audio: {e}")
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping audio test...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
