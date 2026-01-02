"""
Tavily Provider Implementation.
Only uses official Tavily API endpoints.
"""

import os
import logging
from typing import List, Optional, Dict, Any

from ..types import SearchHit, Document, ProviderType
from ..http import SignalsHTTPClient
from ..cache import SignalsCache

logger = logging.getLogger(__name__)


class TavilyProvider:
    """
    Tavily Search API wrapper.
    Docs: https://docs.tavily.com/docs/tavily-api/rest_api
    """

    BASE_URL = "https://api.tavily.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.http = SignalsHTTPClient(
            base_url=self.BASE_URL,
            rate_limit_delay=1.0,  # Respect 1 req/sec roughly to be safe
        )
        self.cache = SignalsCache()
        self.name = "tavily"

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        search_depth: str = "basic",  # "basic" or "advanced"
    ) -> List[SearchHit]:
        """
        Perform a search using Tavily /search endpoint.
        """
        if not self.api_key:
            logger.warning("Tavily API key missing. Skipping search.")
            return []

        # Check Cache
        cache_key_params = {
            "query": query,
            "max": max_results,
            "inc": include_domains,
            "exc": exclude_domains,
            "depth": search_depth,
        }
        cached = self.cache.get(self.name, "search", **cache_key_params)
        if cached:
            return [SearchHit(**hit) for hit in cached]

        # Execute
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
        }
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        try:
            data = self.http.post("/search", json_data=payload)
            results = data.get("results", [])

            hits = []
            for item in results:
                hits.append(
                    SearchHit(
                        url=item.get("url"),
                        title=item.get("title"),
                        snippet=item.get("content"),
                        score=item.get("score", 0.0),
                        published_date=item.get("published_date"),
                        provider=ProviderType.TAVILY,
                        metadata={"raw_score": item.get("score")},
                    )
                )

            # Cache Result (store as dicts)
            self.cache.set(
                [h.__dict__ for h in hits], self.name, "search", **cache_key_params
            )
            return hits

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    def extract(self, urls: List[str]) -> List[Document]:
        """
        Use Tavily extract feature if available (simulated via search q=url or map).
        Actually Tavily has an 'extract' endpoint in beta or via 'include_raw_content' in search.
        For explicit extraction, we will treat this as a specialized search for the URL
        OR use the 'extract' endpoint if documented.

        Official docs imply /extract is a thing for URL lists.
        Let's assume standard POST /extract for now, or fallback to simple GET.

        Actually, simplest way with Tavily is often just passing URLs to context search.
        But let's leave this empty or basic for now, as Firecrawl/Jina are better for pure extraction.

        We will return empty here and prefer other providers, or implement if needed.
        """
        return []
