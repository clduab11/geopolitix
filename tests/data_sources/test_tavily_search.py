"""Tests for Tavily Search integration."""

import pytest
import responses
from src.data_sources.tavily_search import TavilySearchClient


@pytest.fixture
def tavily_client():
    """Create Tavily client for testing."""
    return TavilySearchClient()


@responses.activate
def test_search_news(tavily_client):
    """Test basic news search."""
    # Mock API response
    responses.add(
        responses.POST,
        "https://api.tavily.com/search",
        json={
            "results": [
                {
                    "title": "Test Article",
                    "url": "https://example.com",
                    "content": "Test content",
                    "published_date": "2024-01-15T10:00:00Z",
                }
            ],
            "answer": "Test answer",
            "follow_up_questions": [],
        },
        status=200,
    )

    result = tavily_client.search_news(
        query="geopolitical crisis",
        days=7,
    )

    assert result is not None
    assert "query" in result
    assert "results" in result
    assert len(result["results"]) > 0


@responses.activate
def test_breaking_news_search(tavily_client):
    """Test breaking news search."""
    responses.add(
        responses.POST,
        "https://api.tavily.com/search",
        json={
            "results": [
                {
                    "title": "Breaking News",
                    "url": "https://example.com/breaking",
                    "published_date": "2024-01-15T23:00:00Z",
                }
            ],
            "answer": "Breaking news summary",
        },
        status=200,
    )

    result = tavily_client.breaking_news_search(
        keywords=["conflict", "military"],
        hours=24,
    )

    assert result is not None
    assert "results" in result


@responses.activate
def test_search_country_events(tavily_client):
    """Test country-specific event search."""
    responses.add(
        responses.POST,
        "https://api.tavily.com/search",
        json={
            "results": [
                {
                    "title": "Country Event",
                    "domain": "reuters.com",
                }
            ],
        },
        status=200,
    )

    result = tavily_client.search_country_events(
        country="China",
        event_type="economic",
        days=7,
    )

    assert result is not None


def test_source_credibility_assessment(tavily_client):
    """Test source credibility scoring."""
    # High credibility source
    high_cred_source = {"domain": "reuters.com"}
    score = tavily_client._assess_source_credibility(high_cred_source)
    assert score >= 0.8

    # Government source
    gov_source = {"domain": "state.gov"}
    score = tavily_client._assess_source_credibility(gov_source)
    assert score >= 0.8

    # Unknown source
    unknown_source = {"domain": "unknown-blog.com"}
    score = tavily_client._assess_source_credibility(unknown_source)
    assert score <= 0.7


@responses.activate
def test_validate_event(tavily_client):
    """Test event validation."""
    responses.add(
        responses.POST,
        "https://api.tavily.com/search",
        json={
            "results": [
                {"title": "Event Confirmation 1", "domain": "reuters.com"},
                {"title": "Event Confirmation 2", "domain": "bbc.com"},
                {"title": "Event Confirmation 3", "domain": "apnews.com"},
            ],
        },
        status=200,
    )

    result = tavily_client.validate_event(
        event_description="Military conflict",
        source_count=3,
    )

    assert result is not None
    assert "validated" in result
    assert "credibility_scores" in result


@responses.activate
def test_api_error_handling(tavily_client):
    """Test error handling for API failures."""
    responses.add(
        responses.POST,
        "https://api.tavily.com/search",
        status=500,
    )

    result = tavily_client.search_news(
        query="test query",
        days=1,
    )

    # Should return empty response on error
    assert result is not None
    assert result["results"] == []
