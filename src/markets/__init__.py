"""
Prediction Market Intelligence & Geopolitical Event Forecasting Lab.

This package contains tools for:
- Connecting to prediction market data sources (real and mock).
- Extracting time-series features from market data.
- Training and evaluating forecasting models.
- Backtesting strategies.
"""

from .types import MarketData, Prediction, BacktestResult
from .pipeline import MarketPipeline

__all__ = ["MarketData", "Prediction", "BacktestResult", "MarketPipeline"]
