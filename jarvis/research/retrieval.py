import logging
import time
import re
from typing import List, Dict, Any

logger = logging.getLogger("JARVIS.Research.Retrieval")

class RetrievalEngine:
    """Handles content cleanup, source deduplication, metadata normalization, and credibility scoring."""

    def __init__(self):
        # Credibility weight registry based on TLD / Domain patterns
        self.domain_reputation = {
            ".gov": 1.0,
            ".edu": 0.95,
            ".org": 0.85,
            "wikipedia.org": 0.80,
            "news.google.com": 0.75,
            "reuters.com": 0.90,
            "apnews.com": 0.90,
            "nytimes.com": 0.85,
            "arxiv.org": 0.95,
            "github.com": 0.85,
            "nature.com": 0.95,
            "science.org": 0.95
        }

    def process_sources(self, raw_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cleans, normalizes, deduplicates, and scores candidate sources."""
        processed = []
        seen_urls = set()

        for src in raw_sources:
            # 1. Deduplication
            url = src.get("url", "").strip().lower()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            # 2. Metadata normalization
            title = src.get("title", "Untitled Source").strip()
            snippet = src.get("snippet", "").strip()
            content = src.get("content", "").strip()
            claims = src.get("claims", [])
            provider = src.get("provider", "unknown")

            # 3. Clean content boilerplate
            cleaned_content = self.clean_boilerplate(content)

            # 4. Source Credibility Ranking
            credibility = self.score_credibility(url)

            processed.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "content": cleaned_content,
                "claims": claims,
                "provider": provider,
                "credibility": credibility,
                "retrieved_at": time.time()
            })

        # Sort by credibility score descending
        processed.sort(key=lambda x: x["credibility"], reverse=True)
        return processed

    def clean_boilerplate(self, content: str) -> str:
        """Strips common web page boilerplate elements, navigation headers, and footer lines."""
        if not content:
            return ""
            
        noise_patterns = [
            r"Navbar\b.*?(Home|Contact|About|Login)",
            r"Copyright\s+©\s+\d{4}.*?All\s+Rights\s+Reserved",
            r"Terms\s+of\s+Service\s+\|\s+Privacy\s+Policy",
            r"Follow\s+us\s+on\s+(Twitter|Facebook|LinkedIn|Instagram)"
        ]
        
        cleaned = content
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
            
        return cleaned.strip()

    def score_credibility(self, url: str) -> float:
        """Calculates a credibility score between 0.0 and 1.0 based on URL domains."""
        score = 0.50
        for pattern, weight in self.domain_reputation.items():
            if pattern in url:
                score = max(score, weight)
        return score
