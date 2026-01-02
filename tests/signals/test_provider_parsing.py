"""
Tests for Signals Providers and Core Logic.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from markets.signals.types import ProviderType, Document
from markets.signals.providers.tavily import TavilyProvider
from markets.signals.providers.firecrawl import FirecrawlProvider
from markets.signals.providers.jina import JinaProvider
from markets.signals.cache import SignalsCache


class TestSignalsProviders(unittest.TestCase):
    def setUp(self):
        # Ensure we don't hit real APIs by mocking or env is empty
        # But we will rely on mocking requests
        pass

    @patch("markets.signals.http.SignalsHTTPClient.post")
    def test_tavily_search_parsing(self, mock_post):
        # Mock Response
        mock_response = {
            "results": [
                {
                    "url": "https://example.com",
                    "title": "Example",
                    "content": "Snippet",
                    "score": 0.9,
                    "published_date": "2024-01-01",
                }
            ]
        }
        mock_post.return_value = mock_response

        provider = TavilyProvider(api_key="test")
        # Bypass cache by using unique query or clearing?
        # We Mock cache to ensure we test lookup
        provider.cache = MagicMock()
        provider.cache.get.return_value = None

        hits = provider.search("query")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].url, "https://example.com")
        self.assertEqual(hits[0].provider, ProviderType.TAVILY)
        self.assertEqual(hits[0].score, 0.9)

    @patch("markets.signals.http.SignalsHTTPClient.post")
    def test_firecrawl_scrape_parsing(self, mock_post):
        mock_response = {
            "data": {
                "markdown": "# Header\nContent",
                "metadata": {"title": "Page Title"},
            }
        }
        mock_post.return_value = mock_response

        provider = FirecrawlProvider(api_key="test")
        provider.cache = MagicMock()
        provider.cache.get.return_value = None

        doc = provider.scrape("https://example.com")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.title, "Page Title")
        self.assertIn("# Header", doc.content_markdown)
        self.assertEqual(doc.provider, ProviderType.FIRECRAWL)


class TestSignalsCache(unittest.TestCase):
    def test_cache_keys(self):
        cache = SignalsCache()
        key1 = cache._get_cache_key("test", "op", a=1, b=2)
        key2 = cache._get_cache_key("test", "op", b=2, a=1)
        self.assertEqual(key1, key2)  # Deterministic

        key3 = cache._get_cache_key("test", "op", a=1, b=3)
        self.assertNotEqual(key1, key3)
