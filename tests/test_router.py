import time
import logging
from jarvis.core.logger import setup_logger
from jarvis.brain.brain_manager import BrainManager

# Setup basic logging to console
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestRouter")

def test_intent_classification():
    logger.info("--- Starting Intent Classification Verification ---")
    brain = BrainManager()
    
    test_queries = {
        "Hello there, Jarvis!": "simple",
        "Can you write a python script to parse logs?": "coding",
        "Google the weather forecast for London online": "web_research",
        "Take a webcam frame screenshot": "vision"
    }

    success = True
    for query, expected in test_queries.items():
        intent = brain.router.classify_intent(query)
        logger.info(f"Query: '{query}' -> Intent: '{intent}' (Expected: '{expected}')")
        if intent != expected:
            logger.error("Mismatch detected in intent classifier!")
            success = False
            
    logger.info(f"Classification Checks Passed: {success}\n")
    return success

def test_circuit_breaker_failover():
    logger.info("--- Starting Circuit Breaker Failover Verification ---")
    brain = BrainManager()
    brain.initialize()

    # 1. Normal call (Coding -> ChatGPT)
    logger.info("Sending normal coding request...")
    res1 = brain.generate_response("Write Python code for sorting arrays.")
    logger.info(f"Result: {res1} (Expected: [CHATGPT] prefix)")
    
    # 2. Failure Call #1 (Simulate API crash)
    logger.info("Sending request designed to trigger primary ChatGPT API failure...")
    res2 = brain.generate_response("Write Python code trigger_fail.")
    logger.info(f"Result: {res2} (Expected: fallback to [GEMINI] prefix)")
    
    # Check circuit status
    logger.info(f"ChatGPT Breaker State: {brain.router.circuits['chatgpt'].state} (Fail count: {brain.router.circuits['chatgpt'].failure_count})")

    # 3. Failure Call #2 (Trips the circuit breaker to OPEN)
    logger.info("Sending second failure request to trip the breaker...")
    res3 = brain.generate_response("Write Python code trigger_fail.")
    logger.info(f"Result: {res3}")
    
    # Check circuit status (should be OPEN now)
    state = brain.router.circuits['chatgpt'].state
    logger.info(f"ChatGPT Breaker State: {state} (Expected: OPEN)")
    if state != "OPEN":
        logger.error("Breaker failed to trip to OPEN state!")
        return False

    # 4. Subsequent Call (Should bypass ChatGPT immediately and call fallback model directly)
    logger.info("Sending subsequent normal coding request (Breaker is OPEN, should skip ChatGPT)...")
    res4 = brain.generate_response("Write Python code for binary search.")
    logger.info(f"Result: {res4} (Expected: immediate [GEMINI] call, bypassing ChatGPT)")
    
    logger.info("Circuit Breaker Failover Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS AI Router Integration Tests      ")
    logger.info("==========================================")
    
    test_intent_classification()
    test_circuit_breaker_failover()
