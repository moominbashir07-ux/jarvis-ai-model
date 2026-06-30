# JARVIS AI OS - Release Notes (v1.0)

We are thrilled to announce the official release of **JARVIS AI OS v1.0**. This release transforms JARVIS from a simple voice helper into a production-grade, self-healing, multi-agent desktop automation platform.

---

## 🚀 Key Features in v1.0

### 1. Autonomous Cooperating Agent Framework
* **Multi-Agent Orchestrator**: Uses a Planner agent to decompose high-level user tasks (e.g. "Research chips, create summary, save and locate") into execution graphs.
* **Context Parameters Mapping**: Dynamically merges output contexts (like parsed crawler findings) to feed downstream automation files or visual click coordinates.
* **Supervisor Safeguards**: Monitors task timelines, enforcing retry bounds and executing fallback replanning on timeout limits.

### 2. Intelligent Internet Research Engine
* **Query Intent Planner**: Classifies prompts to determine scraping strategies.
* **Persistent SQLite Caching**: Eliminates redundant internet crawler loops.
* **Reputation Weighted Retrieval**: Automatically weights sources by publication domain credibility (e.g. Nature, Science).
* **Contradiction Check**: Cross-checks facts to identify conflicting timelines (e.g., fusion grid milestones).

### 3. Windows Workspace Automation
* **Clipboard Interface**: Thread-safe Unicode write, read, and clear clipboard tools.
* **Native Recycle Bin**: Integrates with shell operations to support recovery.
* **Window Focus Controller**: Brings applications to the foreground, bypassing OS focusing restrictions.

### 4. Vision System Integration
* **Selectable Grabs**: Captures screenshots of active windows, virtual screens (multi-monitor), and clipboards.
* **OCR Bounding Box coordinates**: Generates detailed layout maps returning exact element coordinates.
* **16x16 Thumbnail Cache**: Grayscales and downscales frames to instantly identify duplicate layouts, bypassing OCR rendering latency.

### 5. Production Resiliency
* **Crash Recovery watchdog**: Catches global exceptions, records dumps, restarts crashed server threads, and reconnects sockets.
* **Auto-Updater Checksums**: Validates manifest hashes and executes rollbacks on write errors.
* **Privacy-respecting Telemetry**: Tracks performance metrics with configurable opt-in/opt-out toggles.

---

## 🔧 Optimizations & Performance Tweaks
* Memory database WAL journal mode enabled.
* Reduced OCR duplicate capture overhead to under 2ms.
* Optimized provider failover timeouts using open/close Circuit Breakers.
