import os
import sys
import logging
from jarvis.core.logger import setup_logger
from jarvis.vision.desktop_understander import DesktopUnderstandingEngine

setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestDesktopUnderstanding")

def test_desktop_understanding_pipeline():
    logger.info("==========================================")
    logger.info("  Desktop Understanding (Phase D) Test    ")
    logger.info("==========================================")

    engine = DesktopUnderstandingEngine()

    # 1. Window Hierarchy Query
    logger.info("Testing visible window hierarchy scan...")
    windows = engine.get_visible_window_hierarchy()
    logger.info(f"Scan returned {len(windows)} visible windows.")
    if not windows:
        logger.error("No visible windows found on system!")
        return False
    logger.info(f"First visible window details: {windows[0]}")
    for key in ("hwnd", "title", "left", "top", "width", "height"):
        if key not in windows[0]:
            logger.error(f"Missing key in window hierarchy: {key}")
            return False

    # 2. Accessibility Controls Query
    logger.info("Testing accessibility controls parser...")
    controls = engine.get_accessibility_controls()
    logger.info(f"Accessibility Controls parsed: {controls}")
    if not controls:
        logger.error("No accessibility controls found!")
        return False
    for key in ("type", "name", "left", "top", "width", "height", "enabled"):
        if key not in controls[0]:
            logger.error(f"Missing key in accessibility control: {key}")
            return False

    # 3. Build Unified Layout Map
    logger.info("Testing multi-modal unified layout synthesis...")
    screenshot_path = "logs/test_active_desktop.png"
    if os.path.exists(screenshot_path):
        try:
            os.remove(screenshot_path)
        except Exception:
            pass
            
    layout = engine.build_desktop_layout_map(screenshot_path=screenshot_path)
    logger.info(f"Layout synthesized keys: {list(layout.keys())}")
    for key in ("windows", "ocr_text_blocks", "interactive_controls", "timestamp"):
        if key not in layout:
            logger.error(f"Missing key in layout map: {key}")
            return False
    logger.info("Unified Layout Map: [PASS]")

    # 4. Geometric coordinate matches
    logger.info("Testing geometric semantic coordinate matcher...")
    # Point (460, 310) -> Should bound button "Save" (left=450, top=300, w=50, h=25)
    matched = engine.get_semantic_element_at(460, 310, layout_map=layout)
    logger.info(f"Matched element at (460, 310): {matched}")
    if not matched or matched["source"] != "ACCESSIBILITY" or matched["element"]["name"] != "Save":
        logger.error("Coordinate mapping failed to identify Save button control!")
        return False

    # Point (15, 20) -> Should bound FileExplorer window (left=10, top=15, w=400, h=300)
    matched_window = engine.get_semantic_element_at(15, 20, layout_map=layout)
    logger.info(f"Matched element at (15, 20): {matched_window}")
    if not matched_window or matched_window["element"].get("title") != "FileExplorer" and matched_window["element"].get("text") != "FileExplorer":
        logger.error("Coordinate mapping failed to identify FileExplorer container!")
        return False

    # Point (25, 560) -> Should bound OCR block "Settings" (left=20, top=550, w=70, h=20)
    matched_ocr = engine.get_semantic_element_at(25, 560, layout_map=layout)
    logger.info(f"Matched element at (25, 560): {matched_ocr}")
    if not matched_ocr or matched_ocr["source"] != "OCR" or matched_ocr["element"]["text"] != "Settings":
        logger.error("Coordinate mapping failed to identify Settings OCR block!")
        return False

    # Clean up test screenshots
    if os.path.exists(screenshot_path):
        try:
            os.remove(screenshot_path)
        except Exception:
            pass

    logger.info("Desktop Understanding (Phase D) Verification Complete: [PASS]\n")
    return True

if __name__ == "__main__":
    success = test_desktop_understanding_pipeline()
    sys.exit(0 if success else 1)
