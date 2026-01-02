"""
Tests for Orchestrator logic.
"""

import unittest
from unittest.mock import MagicMock, patch

from markets.signals.orchestrator import SignalsOrchestrator
from markets.signals.types import SearchHit, ProviderType


class TestOrchestrator(unittest.TestCase):
    @patch("markets.signals.orchestrator.TavilyProvider")
    @patch("markets.signals.orchestrator.FirecrawlProvider")
    @patch("markets.signals.orchestrator.JinaProvider")
    def test_dedupe_and_allowlist(self, MockJina, MockFirecrawl, MockTavily):
        # Setup Mocks
        tavily = MockTavily.return_value
        jina = MockJina.return_value
        firecrawl = MockFirecrawl.return_value

        # Return duplicate hits
        tavily.search.return_value = [
            SearchHit(url="https://good.com/1", provider=ProviderType.TAVILY),
            SearchHit(url="https://good.com/1", provider=ProviderType.TAVILY),  # Dupe
            SearchHit(url="https://bad.com/2", provider=ProviderType.TAVILY),
        ]

        # Safe config
        config = {"allowlist": ["good.com"], "max_sources": 5}

        orch = SignalsOrchestrator(config)
        orch.jina = jina
        orch.firecrawl = firecrawl
        orch.tavily = tavily

        # Mock extract calls
        orch.jina.read.return_value = None
        orch.firecrawl.scrape.return_value = None

        pack = orch.build_evidence_pack("query", "run1")

        # 1. Check Dedupe in Search Hits
        urls = sorted([h.url for h in pack.search_hits])
        self.assertEqual(urls, ["https://bad.com/2", "https://good.com/1"])

        # 2. Check Extraction Allowlist
        # good.com should be attempted, bad.com skipped

        # We expect calls to Jina (default fallback) for good.com
        # BUT NOT for bad.com

        # Jina read calls
        jina_calls = [args[0] for args, _ in orch.jina.read.call_args_list]
        self.assertIn("https://good.com/1", jina_calls)
        self.assertNotIn("https://bad.com/2", jina_calls)
