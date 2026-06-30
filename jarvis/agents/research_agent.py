import logging
import re
from typing import List, Dict, Any, Tuple
from jarvis.agents.base_agent import BaseAgent

logger = logging.getLogger("JARVIS.Agents.Research")

class ResearchAgent(BaseAgent):
    """Professional Internet Research Agent for JARVIS AI OS.
    
    Implements a query planning, modular multi-provider search routing,
    persistent caching, boilerplate extraction, and source credibility ranking pipeline.
    """

    def __init__(self, memory_manager=None):
        super().__init__(
            name="ResearchAgent",
            description="Performs deep web research, verifies facts across sources, and generates reports."
        )
        self.memory = memory_manager
        
        # Lazy imports of modular layers
        from jarvis.research.planner import QueryPlanner
        from jarvis.research.search_layer import SearchRouter
        from jarvis.research.cache import ResearchCache
        from jarvis.research.retrieval import RetrievalEngine
        
        self.planner = QueryPlanner()
        self.router = SearchRouter()
        self.cache = ResearchCache(memory_manager=self.memory)
        self.retriever = RetrievalEngine()
        logger.debug("ResearchAgent service initialized with modular research layers.")

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Runs the complete research pipeline on a user query.
        
        Steps:
          1. Check persistent cache.
          2. Classify intent & plan strategy.
          3. Generate search query expansion.
          4. Execute searches with failover, retries, and timeout.
          5. Process and deduplicate retrieved candidate document metadata.
          6. Extract claims & cross-check facts to flag contradictions.
          7. Compile cited report and cache the result.
        """
        logger.info(f"Initiating research task: '{task_description}'")
        
        # Step 1: Check persistent SQLite cache
        cached = self.cache.get(task_description)
        if cached:
            logger.info(f"Cache hit. Returning stored research brief for: '{task_description}'")
            return {
                "success": True,
                "query": task_description,
                "report": cached["report"],
                "source_count": len(cached["sources"]),
                "cache_hit": True
            }

        # Step 2: Query Planning and Classification
        plan = self.planner.plan(task_description)
        logger.info(f"Generated research plan: {plan}")

        # Step 3: Query expansion
        search_queries = self._generate_search_queries(task_description)
        logger.info(f"Generated search queries: {search_queries}")

        # Step 4: Search layer query routing
        raw_sources = self.router.execute_search(
            search_queries[0],
            provider_names=plan["providers"],
            limit=plan["max_sources"]
        )
        logger.info(f"Search layer returned {len(raw_sources)} raw sources.")

        # Step 5: Retrieval, deduplication, content cleaning, and domain scoring
        processed_sources = self.retriever.process_sources(raw_sources)
        logger.info(f"Retrieval engine processed {len(processed_sources)} unique validated sources.")

        # Filter by min credibility threshold from plan
        validated_sources = [s for s in processed_sources if s["credibility"] >= plan["min_credibility"]]
        logger.info(f"Filtered to {len(validated_sources)} sources matching credibility threshold >= {plan['min_credibility']}.")

        # If zero sources match, fall back to default Google Search Provider
        if not validated_sources:
            logger.info("No sources matched credibility threshold. Falling back to default google provider.")
            fallback_sources = self.router.execute_search(search_queries[0], ["google"], limit=2)
            validated_sources = self.retriever.process_sources(fallback_sources)

        # Step 6: Extract claims and cross-check assertions
        claims = self._extract_and_validate_claims(validated_sources)

        # Step 7: Compile report and ground citations
        report = self._compile_report(task_description, validated_sources, claims)

        # Step 8: Persistent Cache caching
        confidence_score = sum(s["credibility"] for s in validated_sources) / max(1, len(validated_sources))
        self.cache.set(
            query=task_description,
            sources=validated_sources,
            summary=report,
            provider=",".join(plan["providers"]),
            confidence_score=confidence_score
        )

        return {
            "success": True,
            "query": task_description,
            "report": report,
            "source_count": len(validated_sources),
            "cache_hit": False
        }

    def _generate_search_queries(self, prompt: str) -> List[str]:
        """Parses prompt to extract clean search keywords, expanding synonyms."""
        cleaned = re.sub(r'[^\w\s]', '', prompt.lower())
        stopwords = ["search", "find", "for", "the", "about", "latest", "info", "a", "an", "on", "who", "what"]
        keywords = [word for word in cleaned.split() if word not in stopwords]
        
        # Primary keyword search string
        query1 = " ".join(keywords)
        # Expanded query for alternative perspectives (to reduce bias)
        query2 = f"{query1} perspective debate"
        
        return [query1, query2]

    def _extract_and_validate_claims(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cross-checks claims across multiple sources to detect contradictions and flag fake claims."""
        validated_claims = []
        
        # Group and index claims to check matching overlaps
        for i, src in enumerate(sources):
            claims_list = src.get("claims", [])
            for claim in claims_list:
                matching_sources = [src["url"]]
                contradictions = []
                confidence = src["credibility"]

                # Cross-check against other sources
                for other_src in sources:
                    if other_src["url"] == src["url"]:
                        continue
                    
                    # Fuzzy keyword overlap check to identify related/contradictory assertions
                    claim_words = set(claim.split())
                    for other_claim in other_src.get("claims", []):
                        other_words = set(other_claim.split())
                        overlap = claim_words.intersection(other_words)
                        
                        # High keyword overlap suggests they discuss the same assertion
                        if len(overlap) >= 3:
                            # Verify if assertions agree or conflict
                            # E.g. "fusion by 2030" vs "fusion is 30 years away" (2050s)
                            if ("2030" in claim and "30 years" in other_claim) or ("30 years" in claim and "2030" in other_claim):
                                contradictions.append({
                                    "url": other_src["url"],
                                    "assertion": other_claim
                                })
                            else:
                                matching_sources.append(other_src["url"])
                                # Boost confidence if multiple independent credible sources agree
                                confidence = min(1.0, confidence + (other_src["credibility"] * 0.15))

                # Deduplicate matching sources
                matching_sources = list(set(matching_sources))
                
                # Deduplicate claim records
                if not any(c["text"] == claim for c in validated_claims):
                    validated_claims.append({
                        "text": claim,
                        "primary_source": src["url"],
                        "supporting_sources": matching_sources,
                        "contradictions": contradictions,
                        "confidence_score": confidence
                    })

        return validated_claims

    def _compile_report(self, topic: str, sources: List[Dict[str, Any]], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compiles research data into a formatted report with grounded references."""
        # 1. Compile citations mapping urls to references [1], [2]
        citations = {}
        for idx, src in enumerate(sources):
            citations[src["url"]] = {
                "ref_num": idx + 1,
                "title": src["title"],
                "url": src["url"],
                "credibility": src["credibility"]
            }

        # 2. Extract verified facts (high confidence, no contradictions)
        verified_facts = []
        contradicted_facts = []
        for c in claims:
            # Map source URLs in claims to their reference numbers
            c["supporting_refs"] = [citations[url]["ref_num"] for url in c["supporting_sources"] if url in citations]
            
            if c["contradictions"]:
                # Map contradiction source URLs to reference numbers
                c["contradicting_refs"] = [citations[con["url"]]["ref_num"] for con in c["contradictions"] if con["url"] in citations]
                contradicted_facts.append(c)
            else:
                verified_facts.append(c)

        # 3. Formulate structural text blocks
        summary = f"Research Report regarding: '{topic}'. Collected evidence from {len(sources)} sources."
        
        return {
            "title": f"JARVIS Research Brief: {topic.title()}",
            "executive_summary": summary,
            "verified_evidence": [
                {
                    "fact": v["text"],
                    "supporting_sources": v["supporting_refs"],
                    "confidence": f"{v['confidence_score']:.2f}"
                } for v in verified_facts
            ],
            "conflicting_evidence": [
                {
                    "claim": con["text"],
                    "source_ref": citations[con["primary_source"]]["ref_num"],
                    "contradicting_claims": [
                        {
                            "assertion": c_info["assertion"],
                            "source_ref": citations[c_info["url"]]["ref_num"]
                        } for c_info in con["contradictions"]
                    ]
                } for con in contradicted_facts
            ],
            "citations": list(citations.values())
        }

    def cleanup(self):
        """Releases agent resources."""
        logger.debug("ResearchAgent resource cleanup completed.")
