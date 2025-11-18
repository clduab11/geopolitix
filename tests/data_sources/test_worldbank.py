"""Tests for World Bank API client."""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.data_sources.worldbank import WorldBankClient


class TestWorldBankClient:
    """Test cases for WorldBankClient."""

    def test_init(self):
        """Test client initialization."""
        client = WorldBankClient()
        assert "worldbank" in client.base_url.lower()

    @patch.object(WorldBankClient, "get")
    def test_get_indicator(self, mock_get):
        """Test getting indicator data."""
        mock_get.return_value = [
            {"page": 1, "total": 1},
            [
                {
                    "country": {"value": "United States"},
                    "value": 1.5,
                    "date": "2022",
                }
            ],
        ]

        client = WorldBankClient()
        result = client.get_indicator("PV.EST", "USA")

        assert result is not None
        assert len(result) == 1
        assert result[0]["value"] == 1.5

    @patch.object(WorldBankClient, "get")
    def test_get_political_stability(self, mock_get):
        """Test getting political stability data."""
        mock_get.return_value = [
            {},
            [
                {
                    "country": {"value": "Germany"},
                    "value": 0.85,
                    "date": "2022",
                }
            ],
        ]

        client = WorldBankClient()
        result = client.get_political_stability("DEU")

        assert result["country"] == "Germany"
        assert result["value"] == 0.85
        assert result["indicator"] == "Political Stability"

    @patch.object(WorldBankClient, "get")
    def test_get_governance_indicators(self, mock_get):
        """Test getting all governance indicators."""
        mock_get.return_value = [
            {},
            [
                {
                    "country": {"value": "Test Country"},
                    "value": 0.5,
                    "date": "2022",
                }
            ],
        ]

        client = WorldBankClient()
        result = client.get_governance_indicators("TST")

        assert "indicators" in result
        assert "query_time" in result

    @patch.object(WorldBankClient, "get_governance_indicators")
    def test_calculate_governance_risk_score(self, mock_get_gov):
        """Test governance risk score calculation."""
        mock_get_gov.return_value = {
            "indicators": {
                "Political Stability": {"value": 0.5, "year": "2022"},
                "Rule of Law": {"value": 0.3, "year": "2022"},
            }
        }

        client = WorldBankClient()
        score = client.calculate_governance_risk_score("TST")

        # Score should be between 0 and 100
        assert 0 <= score <= 100

    @patch.object(WorldBankClient, "get_governance_indicators")
    def test_calculate_governance_risk_score_no_data(self, mock_get_gov):
        """Test governance risk score with no data."""
        mock_get_gov.return_value = {"indicators": {}}

        client = WorldBankClient()
        score = client.calculate_governance_risk_score("TST")

        # Should return default moderate risk
        assert score == 50.0

    @patch.object(WorldBankClient, "get")
    def test_get_country_list(self, mock_get):
        """Test getting country list."""
        mock_get.return_value = [
            {},
            [
                {
                    "id": "USA",
                    "iso2Code": "US",
                    "name": "United States",
                    "region": {"value": "North America"},
                    "incomeLevel": {"value": "High income"},
                },
                {
                    "id": "1W",
                    "name": "World",
                    "region": {"value": "Aggregates"},
                },
            ],
        ]

        client = WorldBankClient()
        result = client.get_country_list()

        # Should exclude aggregates
        assert len(result) == 1
        assert result[0]["name"] == "United States"

    @patch.object(WorldBankClient, "get_indicator")
    def test_get_historical_trend(self, mock_get_ind):
        """Test getting historical trend data."""
        mock_get_ind.return_value = [
            {"value": 0.5, "date": "2022"},
            {"value": 0.4, "date": "2021"},
            {"value": 0.3, "date": "2020"},
        ]

        client = WorldBankClient()
        result = client.get_historical_trend("USA", "PV.EST", years=3)

        assert isinstance(result, pd.DataFrame)
        assert "year" in result.columns
        assert "value" in result.columns
