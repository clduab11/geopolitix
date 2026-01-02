"""
Basic feature extraction strategies.
"""

import pandas as pd
from typing import List
from ..types import MarketData


class BasicFeatureExtractor:
    """Extracts simple time-series features."""

    def __init__(self, windows: List[int] = [7, 30]):
        self.windows = windows

    def fit_transform(self, market_data: MarketData) -> pd.DataFrame:
        """
        Enhance the data dataframe with features.
        Returns a new dataframe with added feature columns.
        """
        df = market_data.data.copy()
        df = df.sort_values("timestamp")

        if "price" not in df.columns:
            return df

        # Returns
        df["return"] = df["price"].pct_change()

        for w in self.windows:
            # Rolling Mean
            df[f"rolling_mean_{w}"] = df["price"].rolling(window=w).mean()
            # Rolling Volatility (Std Dev)
            df[f"rolling_vol_{w}"] = df["price"].rolling(window=w).std()

        # Fill NaNs resulting from rolling windows
        df = df.bfill().fillna(0)

        return df
