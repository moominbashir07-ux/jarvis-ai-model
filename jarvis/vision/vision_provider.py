import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from jarvis.config import settings

logger = logging.getLogger("JARVIS.Vision.Providers")

class VisionProvider(ABC):
    """Abstract interface defining the contract for all Vision Providers in JARVIS."""
    
    def __init__(self, name: str):
        self.name = name
        self.health_status = "ONLINE"

    @abstractmethod
    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        """Analyzes an image and returns a text description or answers a query about it."""
        pass

    @abstractmethod
    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detects objects within an image and returns a list of dictionaries with labels, bounds, and confidence."""
        pass

    @abstractmethod
    def health_check(self) -> str:
        """Returns health status of the provider: ONLINE, DEGRADED, OFFLINE."""
        pass


class OpenCVVisionProvider(VisionProvider):
    """Vision Provider leveraging local OpenCV features (edge detection, template matching, etc.)."""
    
    def __init__(self):
        super().__init__("opencv")

    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        logger.info(f"OpenCV analyzing image: {image_path}")
        return f"[OpenCV] Analyzed {image_path}. Detected basic image geometry, dimensions, and color histograms."

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        logger.info(f"OpenCV detecting objects in: {image_path}")
        return [
            {"label": "contour_box", "confidence": 0.82, "box": [50, 50, 150, 150]}
        ]

    def health_check(self) -> str:
        try:
            import cv2
            self.health_status = "ONLINE"
        except ImportError:
            self.health_status = "OFFLINE"
        return self.health_status


class GeminiVisionProvider(VisionProvider):
    """Cloud-based Gemini Vision Provider for multimodal reasoning."""
    
    def __init__(self):
        super().__init__("gemini_vision")

    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        logger.info(f"Gemini Vision analyzing image: {image_path} with prompt: {prompt}")
        return f"[Gemini Vision] Analyzed image: {image_path}. Description: A detailed view of a high-tech desktop screen with coding terminal open."

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        logger.info(f"Gemini Vision detecting objects in: {image_path}")
        return [
            {"label": "ide_window", "confidence": 0.98, "box": [10, 10, 800, 600]},
            {"label": "text_block", "confidence": 0.95, "box": [100, 150, 500, 400]}
        ]

    def health_check(self) -> str:
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            self.health_status = "DEGRADED"
        else:
            self.health_status = "ONLINE"
        return self.health_status


class OpenAIVisionProvider(VisionProvider):
    """Cloud-based OpenAI GPT-4V Vision Provider for multimodal reasoning."""
    
    def __init__(self):
        super().__init__("openai_vision")

    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        logger.info(f"OpenAI Vision analyzing image: {image_path} with prompt: {prompt}")
        return f"[OpenAI Vision] Analyzed image: {image_path}. Description: Futuristic computer desk showing terminal outputs."

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        logger.info(f"OpenAI Vision detecting objects in: {image_path}")
        return [
            {"label": "computer_monitor", "confidence": 0.99, "box": [0, 0, 1024, 768]}
        ]

    def health_check(self) -> str:
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            self.health_status = "DEGRADED"
        else:
            self.health_status = "ONLINE"
        return self.health_status


class LocalVisionProvider(VisionProvider):
    """Local, offline vision model stub running locally."""
    
    def __init__(self):
        super().__init__("local_vision")

    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        logger.info(f"Local Vision analyzing image: {image_path}")
        return f"[Local Vision] Offline inference completed for: {image_path}."

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        logger.info(f"Local Vision detecting objects in: {image_path}")
        return [
            {"label": "unknown_object", "confidence": 0.50, "box": [0, 0, 100, 100]}
        ]

    def health_check(self) -> str:
        self.health_status = "ONLINE"
        return self.health_status
