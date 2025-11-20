"""Tests for Intelligence Aggregator."""

import pytest
from unittest.mock import patch
from src.intelligence.aggregator import IntelligenceAggregator


@pytest.fixture
def aggregator():
    """Create Intelligence Aggregator for testing."""
    return IntelligenceAggregator()


@patch("src.intelligence.aggregator.TavilySearchClient")
@patch("src.intelligence.aggregator.ExaSearchClient")
@patch("src.intelligence.aggregator.FirecrawlClient")
@patch("src.intelligence.aggregator.PerplexityFinanceClient")
@patch("src.intelligence.aggregator.SonarReasoningClient")
@patch("src.intelligence.aggregator.NewsAPIClient")
def test_comprehensive_country_analysis(
    mock_newsapi,
    mock_sonar,
    mock_finance,
    mock_firecrawl,
    mock_exa,
    mock_tavily,
    aggregator,
):
    """Test comprehensive country analysis."""
    # Mock responses
    mock_tavily.return_value.search_country_events.return_value = {
        "results": [{"title": "Test news"}]
    }
    mock_exa.return_value.find_similar_events.return_value = {
        "similar_events": []
    }
    mock_firecrawl.return_value.monitor_government_site.return_value = {
        "results": []
    }
    mock_finance.return_value.get_market_impact.return_value = {
        "market_data": "test"
    }
    mock_newsapi.return_value.get_country_news.return_value = {
        "articles": [{"title": "Article 1"}]
    }
    mock_sonar.return_value.synthesize_news.return_value = {
        "summary": "Test summary"
    }
    mock_sonar.return_value.deep_dive_analysis.return_value = {
        "analysis": "Test analysis"
    }

    result = aggregator.comprehensive_country_analysis(
        country="China",
        include_financial=True,
        include_historical=True,
    )

    assert result is not None
    assert "country" in result
    assert result["country"] == "China"
    assert "data_sources" in result


@patch("src.intelligence.aggregator.TavilySearchClient")
@patch("src.intelligence.aggregator.NewsAPIClient")
@patch("src.intelligence.aggregator.SonarReasoningClient")
def test_breaking_news_monitor(
    mock_sonar,
    mock_newsapi,
    mock_tavily,
    aggregator,
):
    """Test breaking news monitoring."""
    # Mock responses
    mock_tavily.return_value.breaking_news_search.return_value = {
        "results": [{"title": "Breaking"}]
    }
    mock_newsapi.return_value.get_geopolitical_news.return_value = {
        "articles": []
    }
    mock_sonar.return_value.prioritize_alerts.return_value = {
        "prioritization": "Test"
    }

    result = aggregator.breaking_news_monitor(
        keywords=["conflict", "crisis"],
        hours=24,
    )

    assert result is not None
    assert "keywords" in result
    assert "prioritized_alerts" in result


@patch("src.intelligence.aggregator.SonarReasoningClient")
def test_generate_executive_brief(mock_sonar, aggregator):
    """Test executive brief generation."""
    mock_sonar.return_value.generate_executive_brief.return_value = {
        "brief": "Test executive brief",
        "timeframe": "24h",
    }

    result = aggregator.generate_executive_brief(
        timeframe="24h",
        focus_regions=["Middle East"],
    )

    assert result is not None
    assert "brief" in result


def test_timeframe_conversion(aggregator):
    """Test timeframe to days conversion."""
    assert aggregator._timeframe_to_days("24h") == 1
    assert aggregator._timeframe_to_days("7d") == 7
    assert aggregator._timeframe_to_days("30d") == 30


def test_country_code_conversion(aggregator):
    """Test country name to code conversion."""
    assert aggregator._get_country_code("United States") == "US"
    assert aggregator._get_country_code("United Kingdom") == "UK"
    assert aggregator._get_country_code("China") == "CN"
    # Unknown country should return first 2 chars uppercased
    assert len(aggregator._get_country_code("Unknown")) == 2


@patch("src.intelligence.aggregator.TavilySearchClient")
@patch("src.intelligence.aggregator.ExaSearchClient")
@patch("src.intelligence.aggregator.NewsAPIClient")
def test_multi_source_search(
    mock_newsapi,
    mock_exa,
    mock_tavily,
    aggregator,
):
    """Test multi-source search."""
    mock_tavily.return_value.search_news.return_value = {"results": []}
    mock_exa.return_value.neural_search.return_value = {"results": []}
    mock_newsapi.return_value.get_geopolitical_news.return_value = {
        "articles": []
    }

    result = aggregator.multi_source_search(
        query="Iran sanctions",
        include_financial=False,
    )

    assert result is not None
    assert "query" in result
    assert "sources" in result
    assert "tavily" in result["sources"]
    assert "exa" in result["sources"]


@patch("src.intelligence.aggregator.TavilySearchClient")
@patch("src.intelligence.aggregator.ExaSearchClient")
@patch("src.intelligence.aggregator.SonarReasoningClient")
def test_validate_event_multi_source(
    mock_sonar,
    mock_exa,
    mock_tavily,
    aggregator,
):
    """Test multi-source event validation."""
    mock_tavily.return_value.validate_event.return_value = {
        "validated": True,
        "sources": [1, 2, 3],
    }
    mock_exa.return_value.find_similar_events.return_value = {
        "similar_events": []
    }
    mock_sonar.return_value.causal_inference.return_value = {
        "causal_analysis": "Test"
    }

    result = aggregator.validate_event_multi_source(
        event_description="Military coup",
        min_sources=3,
    )

    assert result is not None
    assert "validated" in result
    assert "ai_analysis" in result
