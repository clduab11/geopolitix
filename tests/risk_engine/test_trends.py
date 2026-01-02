import pytest
from src.risk_engine.trends import TrendAnalyzer


class TestTrendAnalyzer:
    def test_analyze_empty(self):
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_trend([])
        assert result["velocity"] == 0.0
        assert result["direction"] == "stable"

    def test_analyze_single(self):
        analyzer = TrendAnalyzer()
        result = analyzer.analyze_trend([50.0])
        assert result["velocity"] == 0.0

    def test_analyze_stable(self):
        analyzer = TrendAnalyzer()
        history = [50.0, 50.5, 50.2]
        result = analyzer.analyze_trend(history)
        assert result["velocity"] == -0.3
        assert result["direction"] == "stable"

    def test_analyze_increasing(self):
        analyzer = TrendAnalyzer()
        history = [50.0, 52.0, 55.0]
        result = analyzer.analyze_trend(history)
        assert result["velocity"] == 3.0
        assert result["direction"] == "increasing"

    def test_analyze_rapidly_increasing(self):
        analyzer = TrendAnalyzer()
        history = [50.0, 55.0, 65.0]
        result = analyzer.analyze_trend(history)
        assert result["velocity"] == 10.0
        assert result["direction"] == "rapidly_increasing"

    def test_analyze_decreasing(self):
        analyzer = TrendAnalyzer()
        history = [50.0, 48.0, 46.0]
        result = analyzer.analyze_trend(history)
        assert result["velocity"] == -2.0
        assert result["direction"] == "decreasing"

    def test_analyze_acceleration(self):
        analyzer = TrendAnalyzer()
        # V1 = 52-50 = 2
        # V2 = 56-52 = 4
        # A = 4 - 2 = 2
        history = [50.0, 52.0, 56.0]
        result = analyzer.analyze_trend(history)
        assert result["acceleration"] == 2.0
