import logging
from typing import Dict, Any

logger = logging.getLogger("JARVIS.Distributed.MobileGateway")

class MobileGateway:
    """Manages audio streams inputs and camera frames from mobile companion devices."""

    def __init__(self):
        self.stream_active = False

    def handle_mobile_connection(self, device_id: str) -> bool:
        logger.info(f"Establishing companion session for mobile device: '{device_id}'")
        self.stream_active = True
        return True
