"""
Mock Connector for testing and development.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

from .base import BaseConnector
from ..types import MarketData


class MockConnector(BaseConnector):
    """Generates deterministic synthetic market data."""

    def __init__(self, seed: int = 42, config: dict = None):
        super().__init__(config)
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def fetch_history(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> MarketData:
        """
        Generate a random walk price series.
        """
        end = end_date or datetime.now()
        start = start_date or (end - timedelta(days=90))

        dates = pd.date_range(start=start, end=end, freq="D")
        n = len(dates)

        # Geometric Brownian Motion-ish
        # Start at 0.5 (probability-like)
        prices = [0.5]
        for _ in range(n - 1):
            change = self.rng.normal(0, 0.05)  # mean 0, std 0.05
            new_price = prices[-1] + change
            new_price = max(0.01, min(0.99, new_price))  # Clamp between 0 and 1
            prices.append(new_price)

        df = pd.DataFrame(
            {
                "timestamp": dates,
                "price": prices,
                "volume": self.rng.integers(1000, 10000, n),
            }
        )

        return MarketData(
            market_id=f"mock-{symbol}",
            symbol=symbol,
            source="mock",
            data=df,
            metadata={"seed": self.seed},
        )
