from enum import Enum

class RuntimeLifecycle(Enum):
    """Represents the operational phases of the JARVIS OS Master Orchestrator."""
    INITIALIZING = "INITIALIZING"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    SHUTDOWN = "SHUTDOWN"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
