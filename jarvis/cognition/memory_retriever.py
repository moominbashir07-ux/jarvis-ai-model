import logging
from typing import Dict, Any, List

logger = logging.getLogger("JARVIS.Cognition.Memory")

class MemoryRetriever:
    """Performs contextual checks to load only highly relevant memories, avoiding overheads."""

    def __init__(self):
        pass

    def retrieve_relevant_memories(self, query: str, context_keys: List[str]) -> List[str]:
        logger.info(f"Retrieving memories matching context query: '{query}'")
        
        matches = []
        for key in context_keys:
            if any(q in key.lower() for q in query.lower().split()):
                matches.append(key)
                
        logger.info(f"Memory lookup matching: found {len(matches)} contextual memories.")
        return matches
