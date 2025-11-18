"""Tests for data transformers."""

import pytest
import pandas as pd

from src.utils.transformers import (
    iso_to_country,
    country_to_iso,
    normalize_country_name,
    calculate_risk_change,
    aggregate_risk_scores,
)


class TestIsoToCountry:
    """Test ISO code to country name conversion."""

    def test_valid_code(self):
        """Test valid ISO code conversion."""
        assert iso_to_country("USA") == "United States"
        assert iso_to_country("GBR") == "United Kingdom"
        assert iso_to_country("DEU") == "Germany"

    def test_lowercase(self):
        """Test lowercase code conversion."""
        assert iso_to_country("usa") == "United States"

    def test_invalid_code(self):
        """Test invalid code returns original."""
        assert iso_to_country("XYZ") == "XYZ"


class TestCountryToIso:
    """Test country name to ISO code conversion."""

    def test_valid_name(self):
        """Test valid country name conversion."""
        assert country_to_iso("United States") == "USA"
        assert country_to_iso("Germany") == "DEU"

    def test_invalid_name(self):
        """Test invalid name returns original."""
        assert country_to_iso("Invalid Country") == "Invalid Country"


class TestNormalizeCountryName:
    """Test country name normalization."""

    def test_usa_variations(self):
        """Test USA name variations."""
        assert normalize_country_name("usa") == "United States"
        assert normalize_country_name("united states of america") == "United States"
        assert normalize_country_name("US") == "United States"

    def test_uk_variations(self):
        """Test UK name variations."""
        assert normalize_country_name("uk") == "United Kingdom"
        assert normalize_country_name("great britain") == "United Kingdom"

    def test_other_variations(self):
        """Test other country variations."""
        assert normalize_country_name("russia") == "Russia"
        assert normalize_country_name("russian federation") == "Russia"

    def test_title_case(self):
        """Test that unknown names are title cased."""
        assert normalize_country_name("some country") == "Some Country"


class TestCalculateRiskChange:
    """Test risk change calculation."""

    def test_increase(self):
        """Test calculating increase."""
        result = calculate_risk_change(60.0, 50.0)
        assert result["absolute_change"] == 10.0
        assert result["percentage_change"] == 20.0
        assert result["direction"] == "increase"

    def test_decrease(self):
        """Test calculating decrease."""
        result = calculate_risk_change(40.0, 50.0)
        assert result["absolute_change"] == -10.0
        assert result["percentage_change"] == -20.0
        assert result["direction"] == "decrease"

    def test_stable(self):
        """Test no change."""
        result = calculate_risk_change(50.0, 50.0)
        assert result["absolute_change"] == 0
        assert result["direction"] == "stable"

    def test_from_zero(self):
        """Test change from zero."""
        result = calculate_risk_change(50.0, 0.0)
        assert result["percentage_change"] == 100.0


class TestAggregateRiskScores:
    """Test risk score aggregation."""

    def test_simple_average(self):
        """Test simple average without weights."""
        df = pd.DataFrame({
            "country": ["A", "B", "C"],
            "risk_score": [40, 50, 60],
        })

        result = aggregate_risk_scores(df)
        assert result == 50.0

    def test_weighted_average(self):
        """Test weighted average."""
        df = pd.DataFrame({
            "country": ["A", "B"],
            "risk_score": [40, 60],
            "weight": [0.3, 0.7],
        })

        result = aggregate_risk_scores(df, "weight")
        expected = (40 * 0.3 + 60 * 0.7) / 1.0
        assert abs(result - expected) < 0.01

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=["country", "risk_score"])
        result = aggregate_risk_scores(df)
        assert result == 0.0
