"""
Jina Provider Implementation.
Services: Reader (r.jina.ai), Search (s.jina.ai), Embeddings (api.jina.ai).
"""

import os
import logging
from typing import List, Optional, Dict, Any

from ..types import Document, SearchHit, ProviderType
from ..http import SignalsHTTPClient
from ..cache import SignalsCache

logger = logging.getLogger(__name__)


class JinaProvider:
    """
    Jina AI Services wrapper.
    """

    # Base URLs are different per service, so we use full URLs in requests

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        self.http = SignalsHTTPClient(rate_limit_delay=0.5)
        self.cache = SignalsCache()
        self.name = "jina"

    def read(self, url: str) -> Optional[Document]:
        """
        Convert URL to Markdown via r.jina.ai
        """
        # Cache Check
        cached = self.cache.get(self.name, "read", url=url)
        if cached:
            doc = Document(**cached)
            doc.provider = ProviderType.JINA
            return doc

        target_url = f"https://r.jina.ai/{url}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Jina Reader params via headers
        headers["X-Retain-Images"] = "none"

        try:
            # r.jina.ai returns raw text/markdown usually
            text_content = self.http.get(target_url, headers=headers)
            if not text_content or not isinstance(text_content, str):
                # Sometimes it might return json error
                return None

            # Simple parsing of title? r.jina.ai puts Title: ... at top often
            # For now just dump content
            doc = Document(
                url=url,
                content_markdown=text_content,
                title=None,
                provider=ProviderType.JINA,
            )

            doc_dict = doc.__dict__.copy()
            doc_dict["provider"] = "jina"
            self.cache.set(doc_dict, self.name, "read", url=url)
            return doc

        except Exception as e:
            logger.error(f"Jina read failed for {url}: {e}")
            return None

    def search(self, query: str) -> List[SearchHit]:
        """
        Search via s.jina.ai
        """
        # NO CACHE FOR JINA SEARCH? Let's cache it.
        cached = self.cache.get(self.name, "search", query=query)
        if cached:
            return [SearchHit(**h) for h in cached]

        # s.jina.ai is a GET request returning text/markdown with links?
        # Actually s.jina.ai returns a stream or structured text.
        # Better to strictly use JSON mode if available.
        # Header "Accept: application/json" is supported by s.jina.ai

        url = f"https://s.jina.ai/{query}"
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            data = self.http.get(url, headers=headers)
            if not isinstance(data, dict):
                # Fallback if text returned
                return []

            # Helper to parse Jina JSON response structure
            # { "data": [ { "url": "...", "title": "...", "description": "..." } ] }
            results = data.get("data", [])
            hits = []
            for item in results:
                hits.append(
                    SearchHit(
                        url=item.get("url"),
                        title=item.get("title"),
                        snippet=item.get("description"),
                        score=item.get("score", 0.0) if item.get("score") else 0.0,
                        provider=ProviderType.JINA,
                    )
                )

            self.cache.set([h.__dict__ for h in hits], self.name, "search", query=query)
            return hits

        except Exception as e:
            logger.error(f"Jina search failed: {e}")
            return []

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings from api.jina.ai/v1/embeddings
        """
        if not self.api_key or not texts:
            return []

        # We process in batches of 32 to be safe
        BATCH_SIZE = 32
        all_embeddings = []

        url = "https://api.jina.ai/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]

            # Check cache per text? Too granular for batch API.
            # We'll skip caching embeddings for now to save complexity,
            # or the orchestrator should handle caching unique text chunks.

            payload = {"model": "jina-embeddings-v2-base-en", "input": batch}

            try:
                data = self.http.post(url, json_data=payload, headers=headers)
                if data and "data" in data:
                    # data['data'] is list of {object: embedding, embedding: [...], index: ...}
                    # We need to sort by index just in case
                    sorted_res = sorted(data["data"], key=lambda x: x["index"])
                    all_embeddings.extend([x["embedding"] for x in sorted_res])
            except Exception as e:
                logger.error(f"Jina embed batch failed: {e}")

        return all_embeddings
