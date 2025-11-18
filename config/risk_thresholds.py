"""Risk scoring thresholds and weight configurations."""

from typing import Dict, Tuple


class RiskThresholds:
    """Configuration for risk scoring thresholds and factor weights."""

    # Risk Level Thresholds (0-100 scale)
    RISK_LEVELS: Dict[str, Tuple[int, int]] = {
        "low": (0, 25),
        "moderate": (26, 50),
        "high": (51, 75),
        "critical": (76, 100),
    }

    # Risk Level Colors for visualization
    RISK_COLORS: Dict[str, str] = {
        "low": "#2ecc71",       # Green
        "moderate": "#f39c12",  # Orange
        "high": "#e74c3c",      # Red
        "critical": "#8e44ad",  # Purple
    }

    # Color scale for choropleth (continuous)
    CHOROPLETH_COLORSCALE = [
        [0.0, "#2ecc71"],   # Low - Green
        [0.25, "#f1c40f"],  # Moderate-Low - Yellow
        [0.5, "#f39c12"],   # Moderate - Orange
        [0.75, "#e74c3c"],  # High - Red
        [1.0, "#8e44ad"],   # Critical - Purple
    ]

    # Factor Weights for Composite Risk Score
    FACTOR_WEIGHTS: Dict[str, float] = {
        "political": 0.25,   # Political stability
        "economic": 0.25,    # Economic risk
        "security": 0.30,    # Security/conflict
        "trade": 0.20,       # Trade relations
    }

    # Sub-factor weights within each category
    POLITICAL_SUBFACTORS: Dict[str, float] = {
        "government_stability": 0.30,
        "regime_type": 0.20,
        "corruption": 0.25,
        "rule_of_law": 0.25,
    }

    ECONOMIC_SUBFACTORS: Dict[str, float] = {
        "gdp_growth": 0.25,
        "inflation": 0.20,
        "currency_stability": 0.25,
        "debt_level": 0.30,
    }

    SECURITY_SUBFACTORS: Dict[str, float] = {
        "conflict_intensity": 0.35,
        "terrorism_risk": 0.25,
        "civil_unrest": 0.25,
        "border_security": 0.15,
    }

    TRADE_SUBFACTORS: Dict[str, float] = {
        "tariff_barriers": 0.30,
        "sanctions": 0.35,
        "trade_disputes": 0.20,
        "supply_chain_risk": 0.15,
    }

    # Alert Thresholds
    ALERT_THRESHOLD_CHANGE: int = 10  # Risk score change to trigger alert
    ALERT_THRESHOLD_ABSOLUTE: int = 70  # Absolute score to trigger alert

    # News Sentiment Thresholds
    SENTIMENT_NEGATIVE_THRESHOLD: float = -0.3
    SENTIMENT_POSITIVE_THRESHOLD: float = 0.3

    # Event Severity Mappings
    EVENT_SEVERITY: Dict[str, int] = {
        "low": 10,
        "medium": 30,
        "high": 60,
        "critical": 90,
    }

    @classmethod
    def get_risk_level(cls, score: float) -> str:
        """Get risk level category from numeric score."""
        for level, (low, high) in cls.RISK_LEVELS.items():
            if low <= score <= high:
                return level
        return "critical" if score > 100 else "low"

    @classmethod
    def get_risk_color(cls, score: float) -> str:
        """Get color for a given risk score."""
        level = cls.get_risk_level(score)
        return cls.RISK_COLORS.get(level, cls.RISK_COLORS["moderate"])
