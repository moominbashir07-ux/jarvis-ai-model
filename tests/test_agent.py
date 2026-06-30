import logging
from jarvis.core.logger import setup_logger
from jarvis.agents.research_agent import ResearchAgent

# Setup basic logging to console
setup_logger(log_level_str="DEBUG")
logger = logging.getLogger("TestAgent")

def test_research_agent_pipeline():
    logger.info("--- Starting Research Agent Verification ---")
    agent = ResearchAgent()
    agent.initialize()
    
    # Run research on fusion energy to test cache miss, planning, extraction and compilation
    query = "nuclear fusion net energy gain"
    
    # Clean cache entry for test query to ensure initial run is a cache miss
    try:
        agent.cache.db.execute("DELETE FROM research_cache WHERE query = ?", (query.strip().lower(),))
        agent.cache.db.commit()
    except Exception as e:
        logger.warning(f"Failed to clear cache entry at startup: {e}")
        
    result = agent.run(task_description=query)
    
    # Validate result status
    logger.info(f"Task status success: {result['success']}")
    if not result["success"] or result.get("cache_hit") is True:
        logger.error("Initial research task failed or incorrectly hit cache!")
        return False
        
    # Run identical query again to verify Cache Validation
    logger.info("Executing identical query to verify Cache Validation...")
    result_cache = agent.run(task_description=query)
    logger.info(f"Second query cache hit status: {result_cache.get('cache_hit')} (Expected: True)")
    if not result_cache["success"] or result_cache.get("cache_hit") is not True:
        logger.error("Research Cache hit validation failed!")
        return False
        
    report = result["report"]
    logger.info(f"Report Title: '{report['title']}'")
    logger.info(f"Sources Scraped: {result['source_count']}")
    
    # Validate citations
    logger.info("Checking citations credibility scoring...")
    for cite in report["citations"]:
        logger.info(f" - [{cite['ref_num']}] {cite['title']} (URL: {cite['url']}, Credibility: {cite['credibility']:.2f})")
        
    # Validate verified facts
    logger.info("Checking verified evidence extraction...")
    for verified in report["verified_evidence"]:
        logger.info(f" - Fact: '{verified['fact']}' (Supporting Refs: {verified['supporting_sources']}, Confidence: {verified['confidence']})")
        
    # Validate conflicting evidence (should capture the 2030 vs 30-years timeline conflict)
    logger.info("Checking conflicting timeline evidence detection...")
    logger.info(f"Conflicting Claims Count: {len(report['conflicting_evidence'])}")
    
    for conflict in report["conflicting_evidence"]:
        logger.info(f" - Claim: '{conflict['claim']}' (Source Ref: [{conflict['source_ref']}])")
        for contra in conflict["contradicting_claims"]:
            logger.warning(f"   * CONTRADICTED BY: '{contra['assertion']}' (Source Ref: [{contra['source_ref']}])")
            
    agent.cleanup()
    logger.info("Research Agent Verification Complete.\n")
    return True

if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  JARVIS Research Agent Integration Tests ")
    logger.info("==========================================")
    
    test_research_agent_pipeline()
