"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_risk_data():
    """Sample risk score data for testing."""
    return pd.DataFrame(
        {
            "country": ["United States", "China", "Russia", "Germany", "Brazil"],
            "iso_code": ["USA", "CHN", "RUS", "DEU", "BRA"],
            "composite_score": [35.5, 62.3, 78.1, 28.4, 55.2],
            "risk_level": ["moderate", "high", "critical", "moderate", "high"],
            "political": [30.0, 55.0, 75.0, 25.0, 50.0],
            "economic": [35.0, 60.0, 80.0, 30.0, 55.0],
            "security": [40.0, 70.0, 85.0, 28.0, 60.0],
            "trade": [37.0, 64.0, 72.0, 30.0, 56.0],
        }
    )


@pytest.fixture
def sample_country_news():
    """Sample news data for testing."""
    return {
        "country": "United States",
        "total_results": 100,
        "articles": [
            {
                "title": "Test Article 1",
                "description": "Test description",
                "sentiment": {"polarity": 0.2, "subjectivity": 0.5},
            },
            {
                "title": "Test Article 2",
                "description": "Another description",
                "sentiment": {"polarity": -0.3, "subjectivity": 0.6},
            },
        ],
        "query_time": "2024-01-01T00:00:00",
    }


@pytest.fixture
def sample_exposure_data():
    """Sample company exposure data for testing."""
    return [
        {"country": "United States", "type": "headquarters", "value": 500.0},
        {"country": "China", "type": "manufacturing", "value": 200.0},
        {"country": "Germany", "type": "market", "value": 150.0},
        {"country": "Brazil", "type": "supply_chain", "value": 100.0},
    ]


@pytest.fixture
def mock_api_response():
    """Mock successful API response."""
    return {
        "status": "ok",
        "data": [{"id": 1, "value": 100}],
    }


@pytest.fixture
def mock_session():
    """Mock requests session."""
    with patch("requests.Session") as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


# Finance module fixtures


@pytest.fixture
def sample_stock_quote():
    """Sample stock quote data for testing."""
    return {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "price": 150.50,
        "change": 2.50,
        "change_percent": 1.69,
        "day_low": 148.00,
        "day_high": 151.00,
        "year_low": 124.00,
        "year_high": 178.00,
        "market_cap": 2500000000000,
        "pe_ratio": 28.5,
        "eps": 5.28,
        "volume": 50000000,
        "avg_volume": 45000000,
        "open": 149.00,
        "previous_close": 148.00,
        "exchange": "NASDAQ",
        "timestamp": "2024-01-15T12:00:00",
    }


@pytest.fixture
def sample_company_profile():
    """Sample company profile data for testing."""
    return {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
        "ceo": "Tim Cook",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "country": "US",
        "exchange": "NASDAQ",
        "website": "https://www.apple.com",
        "employees": 164000,
        "market_cap": 2500000000000,
        "beta": 1.2,
        "dividend_yield": 0.005,
        "ipo_date": "1980-12-12",
        "timestamp": "2024-01-15T12:00:00",
    }


@pytest.fixture
def sample_historical_prices():
    """Sample historical price data for testing."""
    return {
        "ticker": "AAPL",
        "period": "1M",
        "historical": [
            {"date": "2024-01-15", "open": 149.0, "high": 151.0, "low": 148.0, "close": 150.5, "volume": 50000000},
            {"date": "2024-01-14", "open": 148.0, "high": 150.0, "low": 147.0, "close": 149.0, "volume": 45000000},
            {"date": "2024-01-13", "open": 147.0, "high": 149.0, "low": 146.0, "close": 148.0, "volume": 40000000},
            {"date": "2024-01-12", "open": 146.0, "high": 148.0, "low": 145.0, "close": 147.0, "volume": 42000000},
            {"date": "2024-01-11", "open": 145.0, "high": 147.0, "low": 144.0, "close": 146.0, "volume": 38000000},
        ],
        "timestamp": "2024-01-15T12:00:00",
    }


@pytest.fixture
def sample_income_statement():
    """Sample income statement data for testing."""
    return {
        "ticker": "AAPL",
        "period": "annual",
        "statements": [
            {
                "date": "2023-12-31",
                "revenue": 383285000000,
                "cost_of_revenue": 214137000000,
                "gross_profit": 169148000000,
                "operating_income": 114301000000,
                "net_income": 96995000000,
                "eps": 6.16,
                "eps_diluted": 6.13,
                "ebitda": 125820000000,
                "gross_margin": 0.44,
                "operating_margin": 0.30,
                "net_margin": 0.25,
            },
            {
                "date": "2022-12-31",
                "revenue": 365817000000,
                "cost_of_revenue": 205074000000,
                "gross_profit": 160743000000,
                "operating_income": 109207000000,
                "net_income": 94680000000,
                "eps": 5.89,
                "eps_diluted": 5.86,
                "ebitda": 120319000000,
                "gross_margin": 0.44,
                "operating_margin": 0.30,
                "net_margin": 0.26,
            },
        ],
        "timestamp": "2024-01-15T12:00:00",
    }


@pytest.fixture
def sample_perplexity_response():
    """Sample Perplexity API response for testing."""
    return {
        "content": "Apple Inc. (AAPL) is currently trading at $150.50, up 1.69% for the day. The company reported strong Q4 earnings with revenue of $119.6 billion, beating analyst expectations.",
        "citations": [
            {"index": 1, "url": "https://www.reuters.com/technology/apple-earnings", "title": "Apple Earnings Report"},
            {"index": 2, "url": "https://www.bloomberg.com/apple-stock", "title": "Apple Stock Analysis"},
        ],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 200,
            "total_tokens": 350,
        },
        "model": "sonar-pro",
        "timestamp": "2024-01-15T12:00:00",
    }


@pytest.fixture
def sample_geographic_segments():
    """Sample geographic revenue segments for testing."""
    return [
        {"region": "Americas", "revenue": 169658000000, "date": "2023-12-31"},
        {"region": "Europe", "revenue": 94294000000, "date": "2023-12-31"},
        {"region": "Greater China", "revenue": 72559000000, "date": "2023-12-31"},
        {"region": "Japan", "revenue": 24257000000, "date": "2023-12-31"},
        {"region": "Rest of Asia Pacific", "revenue": 29375000000, "date": "2023-12-31"},
    ]


@pytest.fixture
def sample_peer_companies():
    """Sample peer companies data for testing."""
    return [
        {"ticker": "MSFT", "name": "Microsoft Corp", "price": 380.50, "change_percent": 0.85, "market_cap": 2800000000000, "pe_ratio": 35.2},
        {"ticker": "GOOGL", "name": "Alphabet Inc", "price": 145.20, "change_percent": -0.32, "market_cap": 1800000000000, "pe_ratio": 25.8},
        {"ticker": "META", "name": "Meta Platforms", "price": 360.80, "change_percent": 1.24, "market_cap": 950000000000, "pe_ratio": 28.4},
    ]
