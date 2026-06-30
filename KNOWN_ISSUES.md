# JARVIS AI OS - Known Issues & Limitations (v1.0)

Here are the known limitations, behaviors, and display details for JARVIS AI OS v1.0.

---

## 🖥️ Screen Grabbing & Display Limitations

### 1. Headless Virtual Environments
* **Issue**: On virtual machines or headless remote nodes, screen-grabbing operations (using `ImageGrab.grab()` or `win32gui.GetForegroundWindow()`) may return `Count: 0` or invalid bounds because no physical display context exists.
* **Workaround**: JARVIS automatically detects display context errors and falls back to rendering grayscale dummy frames to prevent system crashes.

### 2. Foreground Window Focus Restrictions
* **Issue**: Windows OS restricts processes from bringing themselves to the foreground unless they currently hold focus input.
* **Resolution**: JARVIS automatically attaches execution threads to the target window process using `AttachThreadInput` to bypass standard focus restrictions.

---

## 🎤 Audio Configuration Checks

### 1. Missing Input/Output Devices
* **Issue**: If no active microphone or speakers are configured on the host machine, the PyAudio loop fails to initialize.
* **Resolution**: The health diagnostics framework flags audio hardware issues as Degraded and automatically switches STT/TTS inputs to HUD text fallback panels.
