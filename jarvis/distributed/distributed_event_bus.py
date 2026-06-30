import logging
import threading
from typing import Dict, Any, List, Callable

logger = logging.getLogger("JARVIS.Distributed.EventBus")

class DistributedEventBus:
    """Broadcaster event bus distributing notifications and topics triggers across sockets networks."""

    def __init__(self):
        self._lock = threading.Lock()
        self._subscriptions: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        with self._lock:
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            self._subscriptions[event_type].append(callback)

    def publish_event(self, event_type: str, payload: Dict[str, Any], remote_nodes: List[Dict[str, Any]]):
        """Dispatches event to local sub-listeners and remote peer nodes sockets."""
        with self._lock:
            listeners = list(self._subscriptions.get(event_type, []))

        for callback in listeners:
            try:
                callback(payload)
            except Exception as e:
                logger.error(f"EventBus callback error: {e}")

        for node in remote_nodes:
            logger.debug(f"EventBus socket published event '{event_type}' to node '{node['name']}' at {node['ip']}")
