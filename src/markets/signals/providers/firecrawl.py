"""
Firecrawl Provider Implementation.
"""

import os
import logging
import time
from typing import List, Optional, Dict, Any

from ..types import Document, ProviderType
from ..http import SignalsHTTPClient
from ..cache import SignalsCache

logger = logging.getLogger(__name__)


class FirecrawlProvider:
    """
    Firecrawl API v1 wrapper.
    """

    BASE_URL = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.http = SignalsHTTPClient(
            base_url=self.BASE_URL,
            rate_limit_delay=2.0,  # Slower rate limit for crawling
        )
        self.cache = SignalsCache()
        self.name = "firecrawl"

    def scrape(self, url: str) -> Optional[Document]:
        """
        Scrape a single URL using /scrape.
        """
        if not self.api_key:
            return None

        # Check Cache
        cached = self.cache.get(self.name, "scrape", url=url)
        if cached:
            doc = Document(**cached)
            doc.provider = ProviderType.FIRECRAWL  # Re-attach enum
            return doc

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "url": url,
            "formats": ["markdown", "metadata"],
            "onlyMainContent": True,
        }

        try:
            data = self.http.post("/scrape", json_data=payload, headers=headers)

            if not data or "data" not in data:
                logger.warning(f"Firecrawl scrape empty for {url}")
                return None

            res = data["data"]
            markdown = res.get("markdown", "")
            meta = res.get("metadata", {})
            title = meta.get("title") or meta.get("og:title")

            doc = Document(
                url=url,
                content_markdown=markdown,
                title=title,
                provider=ProviderType.FIRECRAWL,
                metadata=meta,
            )

            # Cache (convert enum to str implicitly by __dict__ or custom ser?
            # dataclasses asdict is better, but __dict__ works for simple)
            # We need to handle the Enum serialization for JSON.
            doc_dict = doc.__dict__.copy()
            doc_dict["provider"] = "firecrawl"  # Stringify
            # Fetched_at is datetime, json dumper in cache handles it?
            # Our cache.py uses default=str, so yes.

            self.cache.set(doc_dict, self.name, "scrape", url=url)
            return doc

        except Exception as e:
            logger.error(f"Firecrawl scrape failed for {url}: {e}")
            return None

    def map(self, url: str, limit: int = 50) -> List[str]:
        """
        Map a website to find sub-pages.
        """
        if not self.api_key:
            return []

        cached = self.cache.get(self.name, "map", url=url)
        if cached:
            return cached

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"url": url, "limit": limit}

        try:
            data = self.http.post("/map", json_data=payload, headers=headers)
            if not data or "links" not in data:
                return []

            links = data["links"]
            self.cache.set(links, self.name, "map", url=url)
            return links
        except Exception as e:
            logger.error(f"Firecrawl map failed for {url}: {e}")
            return []
