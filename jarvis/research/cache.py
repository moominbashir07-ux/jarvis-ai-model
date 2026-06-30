import json
import logging
import time
from typing import Dict, Any, List, Optional
from jarvis.config import settings
from jarvis.memory.db_backend import SQLiteBackend

logger = logging.getLogger("JARVIS.Research.Cache")

class ResearchCache:
    """Manages persistent SQLite cache for query results, enabling quick lookup and reuse."""
    
    def __init__(self, memory_manager=None):
        self.memory = memory_manager
        if self.memory:
            self.db = self.memory.db
        else:
            self.db = SQLiteBackend(settings.memory_db_path)
            self.db.connect()
            
        # Ensure the research cache schema is present (self-healing)
        try:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS research_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT UNIQUE NOT NULL,
                    sources TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    provider TEXT NOT NULL,
                    confidence_score REAL NOT NULL
                )
            """)
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_research_cache_query ON research_cache (query);")
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to verify or create research_cache schema: {e}")

    def get(self, query: str, max_age_seconds: float = 86400.0) -> Optional[Dict[str, Any]]:
        """Retrieves cached research results if they exist and are within max_age."""
        try:
            rows = self.db.execute(
                "SELECT sources, summary, timestamp, provider, confidence_score FROM research_cache WHERE query = ?",
                (query.strip().lower(),)
            )
            if not rows:
                return None
                
            sources_json, summary_json, timestamp, provider, confidence_score = rows[0]
            
            # Check age
            age = time.time() - timestamp
            if age > max_age_seconds:
                logger.info(f"Cache expired for query: '{query}' (age: {age:.0f}s > {max_age_seconds}s)")
                return None
                
            logger.info(f"Cache hit for query: '{query}'")
            return {
                "query": query,
                "sources": json.loads(sources_json),
                "report": json.loads(summary_json),
                "timestamp": timestamp,
                "provider": provider,
                "confidence_score": confidence_score
            }
        except Exception as e:
            logger.error(f"Error reading research cache: {e}")
            return None

    def set(self, query: str, sources: List[Dict[str, Any]], summary: Dict[str, Any], provider: str, confidence_score: float) -> bool:
        """Stores research results in the cache."""
        try:
            sources_str = json.dumps(sources)
            summary_str = json.dumps(summary)
            timestamp = time.time()
            
            self.db.execute("""
                INSERT INTO research_cache (query, sources, summary, timestamp, provider, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(query) DO UPDATE SET
                    sources = excluded.sources,
                    summary = excluded.summary,
                    timestamp = excluded.timestamp,
                    provider = excluded.provider,
                    confidence_score = excluded.confidence_score
            """, (query.strip().lower(), sources_str, summary_str, timestamp, provider, confidence_score))
            self.db.commit()
            logger.debug(f"Successfully cached research query: '{query}'")
            return True
        except Exception as e:
            logger.error(f"Error writing to research cache: {e}")
            return False
