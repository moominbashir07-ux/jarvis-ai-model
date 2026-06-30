import logging
import threading
from typing import Dict, Any, List, Callable

logger = logging.getLogger("JARVIS.Agents.Bus")

class AgentCommunicationBus:
    """Thread-safe messaging broker allowing dynamically created agents to pub/sub event frames."""

    def __init__(self):
        self._lock = threading.Lock()
        self._listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribes an execution handler callback to a message topic."""
        with self._lock:
            if topic not in self._listeners:
                self._listeners[topic] = []
            self._listeners[topic].append(callback)
            logger.debug(f"Subscribed callback handler to topic: '{topic}'")

    def publish(self, topic: str, payload: Dict[str, Any]):
        """Publishes/broadcasts a payload frame to all subscribed topic handlers."""
        with self._lock:
            listeners = list(self._listeners.get(topic, []))
            
        if listeners:
            logger.debug(f"Broadcasting message to {len(listeners)} listeners on topic: '{topic}'")
            for listener in listeners:
                try:
                    listener(payload)
                except Exception as e:
                    logger.error(f"Error in pub/sub message dispatch: {e}")
