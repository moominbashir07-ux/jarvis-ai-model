import logging
import threading
from typing import Dict, Any, List, Callable

logger = logging.getLogger("JARVIS.Core.EventRouter")

class EventRouter:
    """Thread-safe event router coordinating notifications transfers between services."""

    def __init__(self):
        self._lock = threading.Lock()
        self._subscriptions: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        with self._lock:
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            self._subscriptions[event_type].append(callback)
            logger.debug(f"Subscribed callback handler to event type: '{event_type}'")

    def publish(self, event_type: str, payload: Dict[str, Any]):
        with self._lock:
            listeners = list(self._subscriptions.get(event_type, []))
            
        if listeners:
            logger.debug(f"Broadcasting event '{event_type}' to {len(listeners)} sub-listeners.")
            for listener in listeners:
                try:
                    listener(payload)
                except Exception as e:
                    logger.error(f"Event dispatch callback failed for type '{event_type}': {e}")
