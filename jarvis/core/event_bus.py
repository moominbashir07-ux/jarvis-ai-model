import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("JARVIS.Core.EventBus")

class EventBus:
    """Centralized, lightweight Event Bus for decoupled module communication in JARVIS AI OS.
    
    Supports regular topic subscriptions as well as wildcard ('*') listener registrations
    to capture system-wide diagnostic flows.
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {}
        logger.debug("Central Event Bus initialized.")

    def subscribe(self, event_type: str, listener: Callable[[str, Dict[str, Any]], None]):
        """Registers a listener callback for a specific event topic or wildcard '*'."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if listener not in self._listeners[event_type]:
            self._listeners[event_type].append(listener)
            logger.debug(f"Subscriber registered for topic '{event_type}': {listener.__name__ if hasattr(listener, '__name__') else listener}")

    def unsubscribe(self, event_type: str, listener: Callable[[str, Dict[str, Any]], None]):
        """Removes a listener callback from a topic registration."""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
                logger.debug(f"Subscriber unregistered from topic '{event_type}'")
            except ValueError:
                pass

    def publish(self, event_type: str, payload: Dict[str, Any] = None):
        """Publishes an event payload to all active topic-specific and wildcard subscribers."""
        payload_data = payload if payload is not None else {}
        logger.debug(f"Publishing event '{event_type}': {payload_data}")

        # Dispatch to topic specific listeners
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    listener(event_type, payload_data)
                except Exception as e:
                    logger.error(f"Error in event listener callback for topic '{event_type}': {e}", exc_info=True)

        # Dispatch to wildcard listeners
        if "*" in self._listeners:
            for listener in self._listeners["*"]:
                try:
                    listener(event_type, payload_data)
                except Exception as e:
                    logger.error(f"Error in wildcard event listener callback: {e}", exc_info=True)
