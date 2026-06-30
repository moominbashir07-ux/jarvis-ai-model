import os
import time
import logging
from pathlib import Path
from jarvis.core.logger import setup_logger
from jarvis.vision.vision_manager import VisionManager, FaceRecognizerAdapter, ObjectDetectorAdapter

# Setup basic logging to console
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestVision")

class MockFaceRecognizer(FaceRecognizerAdapter):
    """Mock Face recognition engine to verify model routing callbacks."""
    
    def initialize_model(self) -> bool:
        logger.info("Mock Face Recognizer Model loaded successfully.")
        return True
        
    def register_face(self, label: str, image_path: str) -> bool:
        logger.info(f"Registered face identity: '{label}' -> {image_path}")
        return True
        
    def process_frame(self, frame) -> dict:
        return {"detected": True, "label": "Sir"}

class MockObjectDetector(ObjectDetectorAdapter):
    """Mock Object Detection engine."""
    
    def initialize_model(self) -> bool:
        logger.info("Mock Object Detector Model loaded successfully.")
        return True
        
    def process_frame(self, frame) -> dict:
        return {"detected": True, "objects": ["laptop", "coffee_cup"]}

def test_vision_perception_lifecycle():
    logger.info("--- Starting Computer Vision Perception Verification ---")
    vision = VisionManager()
    
    # Enable vision explicitly for validation checks
    vision.enabled = True
    
    initialized = vision.initialize()
    logger.info(f"Vision Manager initialized: {initialized}")
    
    # 1. Register Mock Model adapters
    logger.info("Registering AI Model Adapters...")
    face_model = MockFaceRecognizer()
    obj_model = MockObjectDetector()
    vision.register_model_adapters(face=face_model, obj=obj_model)
    
    # 2. Test dynamic inference loops
    logger.info("Simulating frames processing pipeline...")
    # Send mock empty frames to trigger registered adapter inferences
    vision._run_inference(frame=None)
    
    # 3. Test screen capture and OCR
    logger.info("Testing desktop screen capture and OCR text extraction...")
    test_screenshot = "tests/test_screen_grab.png"
    if os.path.exists(test_screenshot):
        os.remove(test_screenshot)
        
    success, filepath, ocr_txt = vision.capture_and_analyze_screen(output_path=test_screenshot)
    logger.info(f"Screen Analysis Status: {success}")
    logger.info(f"Screen Image Path: '{filepath}'")
    logger.info(f"OCR Extracted Output: '{ocr_txt}'")
    
    if not success or not Path(filepath).exists():
         logger.error("Screen capture failed!")
         return False

    # 4. Test detailed OCR text mapping and layout cache
    logger.info("Testing detailed OCR text mapping and visual layout caching...")
    detailed_elements = vision.perform_ocr_detailed(test_screenshot)
    logger.info(f"Detailed OCR Elements Found: {len(detailed_elements)}")
    if len(detailed_elements) > 0:
        logger.info(f"First element: {detailed_elements[0]}")
        
    # Test cache hit speed
    start_time = time.time()
    detailed_cached = vision.perform_ocr_detailed(test_screenshot)
    cache_latency = time.time() - start_time
    logger.info(f"Cached OCR Retrieval Latency: {cache_latency:.6f} seconds")

    # 5. Test active window capture
    logger.info("Testing active window screen clip capture...")
    test_window_shot = "tests/active_window_clip.png"
    w_success, w_path = vision.capture_active_window(output_path=test_window_shot)
    logger.info(f"Active Window Capture success: {w_success} (Saved to: {w_path})")
    if w_success and os.path.exists(w_path):
        os.remove(w_path)

    # 6. Test multi-monitor capture
    logger.info("Testing multi-monitor capture...")
    m_success, m_paths = vision.capture_multi_monitor(output_dir="tests/multi")
    logger.info(f"Multi-monitor screenshots taken: {m_success} (Files: {m_paths})")
    for p in m_paths:
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists("tests/multi"):
        try:
            os.rmdir("tests/multi")
        except Exception:
            pass

    # 7. Test locate text coordinates helper
    logger.info("Testing vision-guided automation locate text on screen helper...")
    found, center_x, center_y = vision.locate_text_on_screen("Save")
    logger.info(f"Locate 'Save' Status: {found} at coordinate: ({center_x}, {center_y})")
    if not found or center_x != 475 or center_y != 312:
        logger.error("Text localization coordinate verification failed!")
        return False

    # Clean up test output
    if os.path.exists(filepath):
        os.remove(filepath)
        
    vision.cleanup()
    logger.info("Computer Vision Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS Computer Vision Engine Tests     ")
    logger.info("==========================================")
    
    test_vision_perception_lifecycle()
