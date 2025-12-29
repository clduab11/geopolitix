"""Tests for finance chart generation functions."""

import pytest

from src.visualization.finance_charts import (
    create_stock_chart,
    create_metrics_chart,
    create_peer_comparison_chart,
    create_geographic_exposure_chart,
    create_financial_statement_chart,
    create_sector_performance_chart,
    create_empty_chart,
    get_risk_color,
    format_number,
    format_percent,
)


class TestCreateStockChart:
    """Test cases for stock chart creation."""

    def test_empty_data_returns_empty_chart(self):
        """Test that empty data returns empty chart."""
        fig = create_stock_chart([], "AAPL", "1M")

        # Check that figure has annotation for no data
        assert len(fig.layout.annotations) > 0

    def test_valid_data_creates_chart(self):
        """Test that valid data creates chart with traces."""
        historical = [
            {"date": "2024-01-15", "open": 149, "high": 151, "low": 148, "close": 150, "volume": 50000000},
            {"date": "2024-01-14", "open": 148, "high": 150, "low": 147, "close": 149, "volume": 45000000},
            {"date": "2024-01-13", "open": 147, "high": 149, "low": 146, "close": 148, "volume": 40000000},
        ]

        fig = create_stock_chart(historical, "AAPL", "1M", "line")

        # Should have traces (price and volume)
        assert len(fig.data) >= 1

    def test_area_chart_type(self):
        """Test area chart creation."""
        historical = [
            {"date": "2024-01-15", "open": 149, "high": 151, "low": 148, "close": 150, "volume": 50000000},
            {"date": "2024-01-14", "open": 148, "high": 150, "low": 147, "close": 149, "volume": 45000000},
        ]

        fig = create_stock_chart(historical, "AAPL", "1M", "area")

        # Should have traces
        assert len(fig.data) >= 1

    def test_candle_chart_type(self):
        """Test candlestick chart creation."""
        historical = [
            {"date": "2024-01-15", "open": 149, "high": 151, "low": 148, "close": 150, "volume": 50000000},
            {"date": "2024-01-14", "open": 148, "high": 150, "low": 147, "close": 149, "volume": 45000000},
        ]

        fig = create_stock_chart(historical, "AAPL", "1M", "candle")

        # Should have traces
        assert len(fig.data) >= 1


class TestCreateMetricsChart:
    """Test cases for metrics chart creation."""

    def test_empty_metrics_returns_empty_chart(self):
        """Test that empty metrics returns empty chart."""
        fig = create_metrics_chart({})

        assert len(fig.layout.annotations) > 0

    def test_valid_metrics_creates_chart(self):
        """Test that valid metrics creates bar chart."""
        metrics = {
            "pe_ratio": 28.5,
            "price_to_sales": 8.0,
            "roe": 0.50,
            "roa": 0.20,
            "debt_to_equity": 1.8,
        }

        fig = create_metrics_chart(metrics)

        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"


class TestCreatePeerComparisonChart:
    """Test cases for peer comparison chart."""

    def test_empty_data_returns_empty_chart(self):
        """Test that empty data returns empty chart."""
        fig = create_peer_comparison_chart({}, [])

        assert len(fig.layout.annotations) > 0

    def test_valid_data_creates_chart(self):
        """Test that valid peer data creates chart."""
        company = {"ticker": "AAPL", "pe_ratio": 28.5}
        peers = [
            {"ticker": "MSFT", "pe_ratio": 35.0},
            {"ticker": "GOOGL", "pe_ratio": 25.0},
        ]

        fig = create_peer_comparison_chart(company, peers, "pe_ratio")

        assert len(fig.data) == 1
        assert len(fig.data[0].x) == 3


class TestCreateGeographicExposureChart:
    """Test cases for geographic exposure chart."""

    def test_empty_segments_returns_empty_chart(self):
        """Test that empty segments returns empty chart."""
        fig = create_geographic_exposure_chart([])

        assert len(fig.layout.annotations) > 0

    def test_valid_segments_creates_pie_chart(self):
        """Test that valid segments creates pie chart."""
        segments = [
            {"region": "Americas", "revenue": 50000000000},
            {"region": "Europe", "revenue": 30000000000},
            {"region": "Asia", "revenue": 20000000000},
        ]

        fig = create_geographic_exposure_chart(segments)

        assert len(fig.data) == 1
        assert fig.data[0].type == "pie"

    def test_segments_with_risk_scores(self):
        """Test geographic chart with risk score overlay."""
        segments = [
            {"region": "Americas", "revenue": 50000000000},
            {"region": "Europe", "revenue": 30000000000},
        ]
        risk_scores = {"Americas": 30, "Europe": 45}

        fig = create_geographic_exposure_chart(segments, risk_scores)

        assert len(fig.data) == 1


class TestCreateFinancialStatementChart:
    """Test cases for financial statement chart."""

    def test_empty_data_returns_empty_chart(self):
        """Test that empty data returns empty chart."""
        fig = create_financial_statement_chart([])

        assert len(fig.layout.annotations) > 0

    def test_valid_data_creates_bar_chart(self):
        """Test that valid statement data creates bar chart."""
        statements = [
            {"date": "2023-12-31", "revenue": 100000000000},
            {"date": "2022-12-31", "revenue": 90000000000},
            {"date": "2021-12-31", "revenue": 80000000000},
        ]

        fig = create_financial_statement_chart(statements, "revenue")

        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"


class TestCreateSectorPerformanceChart:
    """Test cases for sector performance chart."""

    def test_empty_data_returns_empty_chart(self):
        """Test that empty data returns empty chart."""
        fig = create_sector_performance_chart([])

        assert len(fig.layout.annotations) > 0

    def test_valid_data_creates_horizontal_bar_chart(self):
        """Test that valid sector data creates horizontal bar chart."""
        sectors = [
            {"sector": "Technology", "change_percent": 2.5},
            {"sector": "Healthcare", "change_percent": -0.5},
            {"sector": "Financial", "change_percent": 1.2},
        ]

        fig = create_sector_performance_chart(sectors)

        assert len(fig.data) == 1
        assert fig.data[0].orientation == "h"


class TestCreateEmptyChart:
    """Test cases for empty chart creation."""

    def test_creates_chart_with_message(self):
        """Test that empty chart shows message."""
        message = "Custom message"
        fig = create_empty_chart(message)

        assert len(fig.layout.annotations) == 1
        assert fig.layout.annotations[0].text == message

    def test_default_message(self):
        """Test default message for empty chart."""
        fig = create_empty_chart()

        assert fig.layout.annotations[0].text == "No data available"


class TestGetRiskColor:
    """Test cases for risk color mapping."""

    def test_critical_risk_purple(self):
        """Test critical risk returns purple."""
        assert get_risk_color(80) == "#8e44ad"
        assert get_risk_color(100) == "#8e44ad"

    def test_high_risk_red(self):
        """Test high risk returns red."""
        assert get_risk_color(60) == "#e74c3c"
        assert get_risk_color(74) == "#e74c3c"

    def test_moderate_risk_orange(self):
        """Test moderate risk returns orange."""
        assert get_risk_color(40) == "#f39c12"
        assert get_risk_color(49) == "#f39c12"

    def test_low_risk_green(self):
        """Test low risk returns green."""
        assert get_risk_color(10) == "#2ecc71"
        assert get_risk_color(24) == "#2ecc71"

    def test_boundary_values(self):
        """Test boundary values."""
        assert get_risk_color(25) == "#f39c12"  # Moderate starts at 25
        assert get_risk_color(50) == "#e74c3c"  # High starts at 50
        assert get_risk_color(75) == "#8e44ad"  # Critical starts at 75


class TestFormatNumber:
    """Test cases for number formatting."""

    def test_trillion(self):
        """Test trillion formatting."""
        assert format_number(2500000000000) == "$2.50T"

    def test_billion(self):
        """Test billion formatting."""
        assert format_number(2500000000) == "$2.50B"

    def test_million(self):
        """Test million formatting."""
        assert format_number(2500000) == "$2.50M"

    def test_thousand(self):
        """Test thousand formatting."""
        assert format_number(2500) == "$2.50K"

    def test_small_number(self):
        """Test small number formatting."""
        assert format_number(25.5) == "$25.50"

    def test_zero(self):
        """Test zero returns dash."""
        assert format_number(0) == "--"

    def test_none(self):
        """Test None returns dash."""
        assert format_number(None) == "--"

    def test_custom_prefix(self):
        """Test custom prefix."""
        assert format_number(1000000, prefix="") == "1.00M"

    def test_negative_number(self):
        """Test negative number formatting."""
        assert format_number(-2500000000) == "$-2.50B"


class TestFormatPercent:
    """Test cases for percentage formatting."""

    def test_positive_percent(self):
        """Test positive percentage."""
        assert format_percent(5.5) == "+5.50%"

    def test_negative_percent(self):
        """Test negative percentage."""
        assert format_percent(-3.25) == "-3.25%"

    def test_zero_percent(self):
        """Test zero percentage."""
        assert format_percent(0) == "+0.00%"

    def test_none_percent(self):
        """Test None returns dash."""
        assert format_percent(None) == "--"
