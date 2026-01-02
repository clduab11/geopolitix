"""
Orchestrator for the Web Signals Feedforward Layer.
Coordinating search, extraction, and embedding.
"""

import logging
import json
import time
import math
import hashlib
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from .types import EvidencePack, SearchHit, Document, ProviderTrace, ProviderType
from .providers.tavily import TavilyProvider
from .providers.firecrawl import FirecrawlProvider
from .providers.jina import JinaProvider

logger = logging.getLogger(__name__)


class SignalsOrchestrator:
    """
    Main entry point for gathering web signals.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Instantiate Providers
        self.tavily = TavilyProvider()
        self.firecrawl = FirecrawlProvider()
        self.jina = JinaProvider()

        # Performance/Safety Config
        self.max_sources = self.config.get("max_sources", 10)
        self.max_pages_per_domain = self.config.get("max_pages", 3)
        self.allowlist = set(self.config.get("allowlist", []))
        self.chunk_size_chars = self.config.get("chunk_size_chars", 4000)

    def _is_url_allowed(self, url: str) -> bool:
        """Check if URL domain is in allowlist (if active)."""
        if not self.allowlist:
            return False  # Default safe: if allowlist empty, we might Block All or Allow All?
            # User requirement: "Default behavior: safe + small. Domain allowlist... off by default means no crawl"
            # So if allowlist is empty, we act strict -> NO CRAWL unless explicitly allowed.
            # But wait, search results are often diverse.
            # Requirement says: "enforce allowlist (off by default means no crawl, only extraction of top search hits)"
            # Re-reading: "Guardrails: enforce allowlist (off by default means no crawl, only extraction of top search hits)"
            # This implies we can extract search hits, but not crawl DEEPER?
            # Let's interpret: Search Hits are OK to fetch content for?
            # Actually usually allowlist applies to EVERYTHING to be distinct.
            # Let's assume strict allowlist for NOW. If url domain not in allowlist, skip.
            return False

        try:
            domain = urlparse(url).netloc.lower()
            # simple substring check for "reuters.com" in "www.reuters.com"
            for allowed in self.allowlist:
                if allowed in domain:
                    return True
        except:
            pass
        return False

    def _get_provider_preference(self, url: str) -> str:
        """Decide which provider to use for extraction."""
        # Configurable logic could go here
        # For now, prefer Firecrawl for complex sites if configured, else Jina
        if "firecrawl" in self.config.get("default_providers", []):
            return "firecrawl"
        return "jina"

    def build_evidence_pack(
        self, query: str, run_id: str, allowlist_override: Optional[List[str]] = None
    ) -> EvidencePack:
        """
        Execute the full pipeline: Search -> Filter -> Extract -> Embed.
        """
        start_time = time.time()
        traces: List[ProviderTrace] = []

        # Overrides
        if allowlist_override:
            self.allowlist = set(allowlist_override)

        # 1. SEARCH
        # Primary: Tavily
        search_hits: List[SearchHit] = []
        try:
            t0 = time.time()
            hits = self.tavily.search(query, max_results=self.max_sources)
            search_hits.extend(hits)
            traces.append(
                ProviderTrace(
                    provider="tavily",
                    action="search",
                    status="success",
                    duration_ms=(time.time() - t0) * 1000,
                    items_count=len(hits),
                )
            )
        except Exception as e:
            logger.error(f"Search failed: {e}")
            traces.append(
                ProviderTrace(
                    provider="tavily",
                    action="search",
                    status="error",
                    duration_ms=0,
                    items_count=0,
                    error=str(e),
                )
            )

        # Deduplicate hits by URL
        seen_urls = set()
        unique_hits = []
        for h in search_hits:
            if h.url not in seen_urls:
                unique_hits.append(h)
                seen_urls.add(h.url)

        # 2. FILTER & EXTRACT
        documents: List[Document] = []

        # We only process unique hits that match allowlist (if strictly enforced)
        # OR if we decide search hits are implicit allow.
        # Requirement: "enforce allowlist (off by default means no crawl, only extraction of top search hits)"
        # This phrasing is tricky. "only extraction of top search hits" implies we DO extract search hits even if not manually allowlisted?
        # BUT "enforce allowlist" suggests restrictions.
        # Let's take the safest path: Only extract if in allowlist OR if we treat search hits as 'safe' enough?
        # User said: "Default behavior: safe + small... Domain allowlist"
        # Let's enforce allowlist strictly for now. If list is empty/missing, we extract nothing?
        # Better: If allowlist is provided, enforce it. If NOT provided, maybe default to NO extraction?
        # "off by default means no crawl, only extraction of top search hits" -> This sounds like:
        # If allowlist is OFF/Empty -> We extract search hits.
        # If allowlist is ON -> We ONLY extract matches.
        # AND "crawl" (deeper) is only on allowlist?
        # Let's simplify:
        # - Always try to extract top K search hits (limit typically small, e.g. 5).
        # - Only 'Map/Crawl' (finding NEW links) if allowlisted.

        targets = []
        for hit in unique_hits:
            if len(targets) >= self.max_sources:
                break

            # Enforce Allowlist
            # If allowlist is populated, we MUST check.
            # If allowlist is empty, we act per requirement: "off by default means no crawl"
            # But earlier decision: "Strict allowlist". If empty list, we default to blocking?
            # User output: "allowlist (off by default...)"
            # Let's interpret: If allowlist has items, we check. If allowlist is empty, we skip all?
            # Or if allowlist is empty, we allow top hits?
            # Re-reading: "off by default means no crawl, only extraction of top search hits"
            # This implies if allowlist is EMPTY, we DO extraction of top hits.
            # If allowlist is NOT empty, we restrict to it?

            # Let's check `_is_url_allowed`.
            # My `_is_url_allowed` returns False if allowlist is empty.
            # That implies Strict Mode (deny all if empty list).
            # This contradicts "extraction of top search hits" safely.
            # Let's modify logic:
            # If allowlist is provided (len > 0), filter by it.
            # If allowlist is empty (default), allow the hit for extraction?

            if self.allowlist:
                if not self._is_url_allowed(hit.url):
                    continue

            targets.append(hit)

        for hit in targets:
            # Check if we should scrape
            # For now, we scrape everything in top K search hits

            doc = None
            t0 = time.time()
            provider_used = self._get_provider_preference(hit.url)

            try:
                # Prefer Firecrawl if explicitly enabled/preferred
                if provider_used == "firecrawl":
                    doc = self.firecrawl.scrape(hit.url)

                # Fallback to Jina
                if not doc:
                    provider_used = "jina"  # update for trace
                    doc = self.jina.read(hit.url)

                if doc:
                    doc.title = doc.title or hit.title
                    doc.metadata["search_score"] = hit.score
                    documents.append(doc)
                    traces.append(
                        ProviderTrace(
                            provider=provider_used,
                            action="extract",
                            status="success",
                            duration_ms=(time.time() - t0) * 1000,
                            items_count=1,
                        )
                    )
                else:
                    traces.append(
                        ProviderTrace(
                            provider=provider_used,
                            action="extract",
                            status="empty",
                            duration_ms=(time.time() - t0) * 1000,
                            items_count=0,
                        )
                    )

            except Exception as e:
                logger.error(f"Extraction failed for {hit.url}: {e}")
                traces.append(
                    ProviderTrace(
                        provider=provider_used,
                        action="extract",
                        status="error",
                        duration_ms=(time.time() - t0) * 1000,
                        items_count=0,
                        error=str(e),
                    )
                )

        # 3. CHUNK & EMBED
        # Simple chunking
        embedding_count = 0
        if documents and self.jina.api_key:
            all_chunks = []
            doc_map = []  # (doc_idx, chunk_text)

            for doc in documents:
                content = doc.content_markdown or ""
                # Simple split by char limit, respecting simple boundaries if possible?
                # Just fixed size for MVP
                chunks = [
                    content[i : i + self.chunk_size_chars]
                    for i in range(0, len(content), self.chunk_size_chars)
                ]
                doc.chunk_count = len(chunks)
                doc.content_hash = hashlib.md5(content.encode()).hexdigest()

                for c in chunks:
                    if c.strip():
                        all_chunks.append(c)

            # Embed batch
            if all_chunks:
                t0 = time.time()
                try:
                    vectors = self.jina.embed(all_chunks)
                    embedding_count = len(vectors)

                    # Store embeddings logic
                    final_embeddings = []
                    for i, vec in enumerate(vectors):
                        if i < len(all_chunks):
                            final_embeddings.append(
                                {
                                    "index": i,
                                    "vector": vec,
                                    "chunk_text_preview": all_chunks[i][:50],
                                }
                            )

                    traces.append(
                        ProviderTrace(
                            provider="jina",
                            action="embed",
                            status="success",
                            duration_ms=(time.time() - t0) * 1000,
                            items_count=embedding_count,
                        )
                    )
                except Exception as e:
                    logger.error(f"Embedding failed: {e}")
                    traces.append(
                        ProviderTrace(
                            provider="jina",
                            action="embed",
                            status="error",
                            duration_ms=(time.time() - t0) * 1000,
                            items_count=0,
                            error=str(e),
                        )
                    )

        return EvidencePack(
            query=query,
            run_id=run_id,
            search_hits=unique_hits,
            documents=documents,
            embeddings=final_embeddings if "final_embeddings" in locals() else [],
            doc_count=len(documents),
            embedding_count=embedding_count,
            provider_traces=traces,
            config_snapshot=self.config,
        )

    def compute_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Utility for cosine similarity."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
