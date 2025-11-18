"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_risk_data():
    """Sample risk score data for testing."""
    return pd.DataFrame({
        "country": ["United States", "China", "Russia", "Germany", "Brazil"],
        "iso_code": ["USA", "CHN", "RUS", "DEU", "BRA"],
        "composite_score": [35.5, 62.3, 78.1, 28.4, 55.2],
        "risk_level": ["moderate", "high", "critical", "moderate", "high"],
        "political": [30.0, 55.0, 75.0, 25.0, 50.0],
        "economic": [35.0, 60.0, 80.0, 30.0, 55.0],
        "security": [40.0, 70.0, 85.0, 28.0, 60.0],
        "trade": [37.0, 64.0, 72.0, 30.0, 56.0],
    })


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
