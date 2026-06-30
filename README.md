# JARVIS AI OS

JARVIS AI OS is a modular, scalable, Windows-based AI assistant built in Python. It features a cleanly separated, decoupled architecture designed to support a wide range of tasks—from voice interaction and memory retention to computer vision and automation control.

## Project Structure

```text
jarvis/
├── .env                      # Local configuration settings (ignored by git)
├── .env.example              # Configuration template
├── requirements.txt          # Third-party dependencies
├── start.bat                 # Windows startup script
├── README.md                 # Project documentation
└── jarvis/                   # Principal application package
    ├── __init__.py           # Package marker
    ├── main.py               # Main orchestrator entry point
    ├── config/               # App configuration layer
    │   ├── __init__.py
    │   └── settings.py       # Config parsing and validation
    ├── core/                 # Shared core orchestrators and helpers
    │   ├── __init__.py
    │   ├── logger.py         # Advanced logging handler
    │   └── orchestrator.py   # Global systems bus / mediator
    ├── brain/                # AI intelligence and reasoning
    │   ├── __init__.py
    │   └── brain_manager.py  # LLM controller / prompt engine
    ├── voice/                # Audio input/output processing
    │   ├── __init__.py
    │   ├── stt.py            # Speech-to-Text handler
    │   └── tts.py            # Text-to-Speech engine
    ├── memory/               # Short-term and long-term memory
    │   ├── __init__.py
    │   └── memory_manager.py  # SQLite/JSON memory controller
    ├── vision/               # Camera perception & screen analysis
    │   ├── __init__.py
    │   └── vision_manager.py  # OCR / Visual LLM orchestrator
    ├── automation/           # Windows OS automation
    │   ├── __init__.py
    │   └── sys_control.py    # Keyboard, mouse, shell automations
    ├── agents/               # Multi-agent tasks & behaviors
    │   ├── __init__.py
    │   └── base_agent.py     # Extensible agent model
    └── ui/                   # Desktop Interface
        ├── __init__.py
        └── gui_manager.py    # Desktop notification / window management
```

## Features

- **Modular Design**: Every service (Brain, Memory, Voice, Vision, Automation, UI) is defined as a decoupled component. They communicate through the core `Orchestrator`.
- **Robust Logger**: Automatic logging to stdout and rotating files in `logs/` directory.
- **Config-Driven**: Environment-based configurations with safe defaults and auto-validation.
- **Windows Integration**: Optimized scripts for quick virtual environment deployment (`start.bat`).

## Setup and Quick Start

### Option A: The Automatic Way (Windows)

Simply double-click the **`start.bat`** script. 
It will automatically:
1. Verify Python installation.
2. Initialize a Python virtual environment (`.venv`).
3. Check and update dependencies using `pip`.
4. Create your local configuration `.env` file if it's missing.
5. Run the application.

### Option B: The Manual Way (Any OS)

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - **Windows (CMD)**: `.venv\Scripts\activate.bat`
   - **Windows (PowerShell)**: `.venv/Scripts/Activate.ps1`
   - **macOS/Linux**: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
5. Run the assistant:
   ```bash
   python -m jarvis.main
   ```
