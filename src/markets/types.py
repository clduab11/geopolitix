"""
Type definitions for the Markets Lab.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd


@dataclass
class MarketData:
    """Standard container for market data."""

    market_id: str
    symbol: str
    source: str
    data: pd.DataFrame  # Expected cols: timestamp, price, volume, open_interest, etc.
    metadata: Dict[str, Any]


@dataclass
class Prediction:
    """A model prediction."""

    market_id: str
    timestamp: datetime
    model_name: str
    predicted_value: float
    confidence: float
    horizon: str  # e.g., "7d", "1m"
    metadata: Dict[str, Any]


@dataclass
class BacktestResult:
    """Result of a backtest run."""

    model_name: str
    start_date: datetime
    end_date: datetime
    metrics: Dict[str, float]  # e.g., {"brier_score": 0.15, "log_loss": 0.45}
    predictions: List[Prediction]
    config: Dict[str, Any]
