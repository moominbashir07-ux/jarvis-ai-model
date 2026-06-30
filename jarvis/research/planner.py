import re
from typing import Dict, Any, List

class QueryPlanner:
    """Classifies user queries to determine the optimal research strategy."""

    def __init__(self):
        # Category patterns mapping keyword regexes to target categories
        self.patterns = {
            "news": r"\b(news|latest|breaking|today|current|recent|update|updates)\b",
            "academic": r"\b(paper|papers|arxiv|journal|scientific|academic|doi|study|studies)\b",
            "code_research": r"\b(python|javascript|code|github|repo|api|syntax|compile|function|library|sdk|programming)\b",
            "product_comparison": r"\b(vs|compare|comparison|alternative|alternatives|better|reviews|price|pricing)\b",
            "documentation": r"\b(docs|documentation|manual|guide|official|reference)\b",
            "tutorial": r"\b(how to|tutorial|steps|guide|walkthrough|learn)\b",
            "troubleshooting": r"\b(error|bug|issue|fix|crash|fail|failure|exception|warn|warning|logs|log)\b"
        }

    def plan(self, query: str) -> Dict[str, Any]:
        """Classifies the query and generates a research execution plan."""
        query_lower = query.lower()
        category = "multi_source" # Default category

        for cat, pattern in self.patterns.items():
            if re.search(pattern, query_lower):
                category = cat
                break

        # Check for simple fact lookup (short queries)
        if category == "multi_source" and (len(query.split()) <= 4 or any(w in query_lower for w in ["who is", "what is", "where is", "when did"])):
            category = "fact_lookup"

        # Formulate execution strategies
        strategy = {
            "category": category,
            "max_sources": 5,
            "min_credibility": 0.70,
            "providers": ["google"]
        }

        if category == "news":
            strategy["max_sources"] = 4
            strategy["min_credibility"] = 0.75
            strategy["providers"] = ["google_news"]
        elif category == "academic":
            strategy["max_sources"] = 3
            strategy["min_credibility"] = 0.90
            strategy["providers"] = ["arxiv", "google"]
        elif category == "code_research":
            strategy["max_sources"] = 5
            strategy["min_credibility"] = 0.80
            strategy["providers"] = ["github", "google_docs"]
        elif category == "product_comparison":
            strategy["max_sources"] = 6
            strategy["min_credibility"] = 0.70
            strategy["providers"] = ["google"]
        elif category == "documentation":
            strategy["max_sources"] = 4
            strategy["min_credibility"] = 0.85
            strategy["providers"] = ["google_docs"]
        elif category == "tutorial":
            strategy["max_sources"] = 5
            strategy["min_credibility"] = 0.75
            strategy["providers"] = ["google"]
        elif category == "troubleshooting":
            strategy["max_sources"] = 4
            strategy["min_credibility"] = 0.80
            strategy["providers"] = ["google", "github"]
        elif category == "fact_lookup":
            strategy["max_sources"] = 2
            strategy["min_credibility"] = 0.80
            strategy["providers"] = ["google"]

        return strategy
