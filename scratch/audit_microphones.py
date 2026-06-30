import pyaudio

p = pyaudio.PyAudio()
print("=========================================")
print("        MICROPHONE FORENSIC AUDIT        ")
print("=========================================")

# Get default input device
try:
    default_device = p.get_default_input_device_info()
    print(f"Default Input Device Index: {default_device.get('index')}")
    print(f"Default Input Device Name: {default_device.get('name')}")
except Exception as e:
    print(f"Error getting default input device: {e}")
    default_device = None

print("\n--- Available Input Devices ---")
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    device_info = p.get_device_info_by_host_api_device_index(0, i)
    if device_info.get('maxInputChannels') > 0:
        print(f"Index {i} - {device_info.get('name')}")
        print(f"  Channels: {device_info.get('maxInputChannels')}")
        print(f"  Sample Rate: {device_info.get('defaultSampleRate')} Hz")
        print("-----------------------------------------")

p.terminate()
