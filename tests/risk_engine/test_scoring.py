"""Tests for risk scoring algorithms."""

from unittest.mock import patch
import pandas as pd

from src.risk_engine.scoring import RiskScorer, get_default_countries


class TestRiskScorer:
    """Test cases for RiskScorer."""

    def test_init(self):
        """Test scorer initialization."""
        scorer = RiskScorer()
        assert scorer.gdelt is not None
        assert scorer.newsapi is not None
        assert scorer.worldbank is not None
        assert scorer.acled is not None

    @patch.object(RiskScorer, "_calculate_political_score")
    @patch.object(RiskScorer, "_calculate_economic_score")
    @patch.object(RiskScorer, "_calculate_security_score")
    @patch.object(RiskScorer, "_calculate_trade_score")
    def test_calculate_composite_score(
        self, mock_trade, mock_security, mock_economic, mock_political
    ):
        """Test composite score calculation."""
        mock_political.return_value = 40.0
        mock_economic.return_value = 50.0
        mock_security.return_value = 60.0
        mock_trade.return_value = 45.0

        scorer = RiskScorer()
        result = scorer.calculate_composite_score("United States")

        assert "composite_score" in result
        assert "factors" in result
        assert "risk_level" in result
        assert 0 <= result["composite_score"] <= 100

    @patch.object(RiskScorer, "calculate_composite_score")
    def test_get_batch_scores(self, mock_calc):
        """Test batch score calculation."""
        mock_calc.return_value = {
            "country": "Test",
            "iso_code": "TST",
            "composite_score": 50.0,
            "risk_level": "moderate",
            "factors": {
                "political": 50.0,
                "economic": 50.0,
                "security": 50.0,
                "trade": 50.0,
            },
        }

        scorer = RiskScorer()
        result = scorer.get_batch_scores(["Country1", "Country2"])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_get_risk_changes(self):
        """Test risk change analysis."""
        scorer = RiskScorer()
        result = scorer.get_risk_changes(
            "Test Country",
            current_score=60.0,
            historical_scores=[50.0, 52.0, 55.0, 58.0],
        )

        assert result["current"] == 60.0
        assert "change_7d" in result
        assert "change_30d" in result
        assert result["trend"] in ["increasing", "decreasing", "stable"]

    def test_get_risk_changes_no_history(self):
        """Test risk change with no history."""
        scorer = RiskScorer()
        result = scorer.get_risk_changes("Test", 50.0, [])

        assert result["change_7d"] == 0
        assert result["change_30d"] == 0
        assert result["trend"] == "stable"

    def test_generate_alerts(self, sample_risk_data):
        """Test alert generation."""
        scorer = RiskScorer()
        alerts = scorer.generate_alerts(sample_risk_data, threshold=70)

        # Russia should trigger alert (78.1 > 70)
        assert len(alerts) >= 1
        assert any(a["country"] == "Russia" for a in alerts)

    def test_generate_alerts_no_high_risk(self):
        """Test alert generation with no high risk countries."""
        scorer = RiskScorer()
        data = pd.DataFrame({
            "country": ["A", "B"],
            "composite_score": [30.0, 40.0],
            "risk_level": ["moderate", "moderate"],
            "political": [30.0, 40.0],
            "economic": [30.0, 40.0],
            "security": [30.0, 40.0],
            "trade": [30.0, 40.0],
        })

        alerts = scorer.generate_alerts(data, threshold=70)
        assert len(alerts) == 0

    def test_get_primary_factor(self):
        """Test primary factor identification."""
        scorer = RiskScorer()
        row = pd.Series({
            "political": 30.0,
            "economic": 60.0,
            "security": 80.0,
            "trade": 40.0,
        })

        result = scorer._get_primary_factor(row)
        assert result == "security"


class TestGetDefaultCountries:
    """Test default countries list."""

    def test_returns_list(self):
        """Test that function returns a list."""
        countries = get_default_countries()
        assert isinstance(countries, list)

    def test_contains_major_countries(self):
        """Test that major countries are included."""
        countries = get_default_countries()
        assert "United States" in countries
        assert "China" in countries
        assert "Russia" in countries

    def test_minimum_count(self):
        """Test minimum number of countries."""
        countries = get_default_countries()
        assert len(countries) >= 20
