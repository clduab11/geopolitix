"""Tests for chart components."""

import pandas as pd
import plotly.graph_objects as go

from src.visualization.charts import (
    create_trend_chart,
    create_comparison_chart,
    create_correlation_matrix,
    create_scenario_comparison,
    create_exposure_pie,
    create_gauge_chart,
)


class TestCreateTrendChart:
    """Test trend chart creation."""

    def test_creates_figure(self):
        """Test that function creates a Plotly figure."""
        data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10),
                "composite_score": [50 + i for i in range(10)],
                "country": ["USA"] * 10,
            }
        )

        fig = create_trend_chart(data)
        assert isinstance(fig, go.Figure)

    def test_has_threshold_lines(self):
        """Test that threshold lines are added."""
        data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "composite_score": [50, 60, 70, 80, 90],
                "country": ["USA"] * 5,
            }
        )

        fig = create_trend_chart(data)
        # Check for horizontal lines in layout
        assert len(fig.layout.shapes) > 0 or "shapes" not in dir(fig.layout)


class TestCreateComparisonChart:
    """Test comparison chart creation."""

    def test_bar_chart(self, sample_risk_data):
        """Test bar chart creation."""
        fig = create_comparison_chart(
            sample_risk_data, ["United States", "China"], chart_type="bar"
        )
        assert isinstance(fig, go.Figure)

    def test_radar_chart(self, sample_risk_data):
        """Test radar chart creation."""
        fig = create_comparison_chart(
            sample_risk_data, ["United States", "China"], chart_type="radar"
        )
        assert isinstance(fig, go.Figure)


class TestCreateCorrelationMatrix:
    """Test correlation matrix creation."""

    def test_creates_heatmap(self, sample_risk_data):
        """Test that function creates a heatmap."""
        fig = create_correlation_matrix(sample_risk_data)
        assert isinstance(fig, go.Figure)

    def test_empty_data(self):
        """Test with insufficient data."""
        data = pd.DataFrame({"a": [1]})
        fig = create_correlation_matrix(data)
        # Should return empty figure
        assert isinstance(fig, go.Figure)


class TestCreateScenarioComparison:
    """Test scenario comparison chart."""

    def test_creates_comparison(self):
        """Test creating before/after comparison."""
        before = {"political": 40, "economic": 50, "security": 60, "trade": 45}
        after = {"political": 55, "economic": 65, "security": 75, "trade": 60}

        fig = create_scenario_comparison(before, after, "Test Country")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # Before and after traces


class TestCreateExposurePie:
    """Test exposure pie chart."""

    def test_creates_pie(self):
        """Test creating pie chart."""
        data = {
            "Manufacturing": 500,
            "Supply Chain": 300,
            "Market": 200,
        }

        fig = create_exposure_pie(data)
        assert isinstance(fig, go.Figure)


class TestCreateGaugeChart:
    """Test gauge chart creation."""

    def test_creates_gauge(self):
        """Test creating gauge chart."""
        fig = create_gauge_chart(65.5, "Test Score")
        assert isinstance(fig, go.Figure)

    def test_value_bounds(self):
        """Test with extreme values."""
        fig_low = create_gauge_chart(0)
        fig_high = create_gauge_chart(100)

        assert isinstance(fig_low, go.Figure)
        assert isinstance(fig_high, go.Figure)
